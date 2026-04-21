import logging

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import admin_settings
import sheets
from config import ADMIN_IDS, USER_NAMES
from keyboards import (
    main_menu, cancel_kb, settings_menu,
    delete_records_kb, months_kb,
)
from states import AddExpense, DeleteExpense, AdminSettings

logger = logging.getLogger(__name__)
router = Router()


# ── Вспомогательные функции ──────────────────────────────────────────────────

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def get_user_name(user_id: int, fallback: str) -> str:
    return USER_NAMES.get(user_id, fallback or str(user_id))


def format_records(records: list) -> str:
    if not records:
        return "📭 Записей пока нет."
    lines = []
    for i, r in enumerate(records, 1):
        lines.append(
            f"{i}. <b>{r['description']}</b> — {r['amount']} ₸\n"
            f"   👤 {r['user']}  📅 {r['date']}"
        )
    return "\n\n".join(lines)


async def go_main(message: Message, state: FSMContext):
    await state.clear()
    week = admin_settings.get_week()
    month = admin_settings.get_month()
    await message.answer(
        f"🏠 <b>Главное меню</b>\n"
        f"📅 Неделя: <b>{week}</b>  |  🗓 Месяц: <b>{month}</b>",
        reply_markup=main_menu(is_admin(message.from_user.id)),
        parse_mode="HTML",
    )


# ── /start ───────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    sheets.ensure_headers()
    await go_main(message, state)


# ── Отмена (работает из любого состояния) ────────────────────────────────────

@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await go_main(message, state)


# ════════════════════════════════════════════════════════════════════════════
#  ДОБАВЛЕНИЕ ЗАТРАТЫ
# ════════════════════════════════════════════════════════════════════════════

@router.message(F.text == "➕ Добавить затрату")
async def add_expense_start(message: Message, state: FSMContext):
    await state.set_state(AddExpense.waiting_description)
    await message.answer(
        "📝 Введите описание затраты:",
        reply_markup=cancel_kb(),
        parse_mode="HTML",
    )


@router.message(AddExpense.waiting_description)
async def add_expense_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AddExpense.waiting_amount)
    await message.answer(
        "💰 Введите сумму (только цифры):",
        reply_markup=cancel_kb(),
    )


@router.message(AddExpense.waiting_amount)
async def add_expense_amount(message: Message, state: FSMContext):
    # Валидация суммы
    text = message.text.strip().replace(",", ".")
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer(
            "⚠️ Неверный формат. Введите число больше нуля:",
            reply_markup=cancel_kb(),
        )
        return

    data = await state.get_data()
    description = data["description"]
    user_name = get_user_name(message.from_user.id, message.from_user.first_name)
    week = admin_settings.get_week()
    month = admin_settings.get_month()

    success = sheets.append_expense(description, amount, user_name, week, month)

    if success:
        await message.answer(
            f"✅ <b>Затрата добавлена!</b>\n\n"
            f"📌 {description}\n"
            f"💰 {amount:,.2f} ₸\n"
            f"👤 {user_name}  |  Неделя {week}  |  {month}",
            parse_mode="HTML",
        )
    else:
        await message.answer("❌ Ошибка при сохранении. Попробуйте ещё раз.")

    await go_main(message, state)


# ════════════════════════════════════════════════════════════════════════════
#  ПОСЛЕДНИЕ ТРАТЫ
# ════════════════════════════════════════════════════════════════════════════

@router.message(F.text == "📋 Последние траты")
async def show_last_expenses(message: Message, state: FSMContext):
    records = sheets.get_last_n_rows(5)
    text = "📋 <b>Последние 5 записей:</b>\n\n" + format_records(records)
    await message.answer(text, parse_mode="HTML")
    await go_main(message, state)


# ════════════════════════════════════════════════════════════════════════════
#  УДАЛЕНИЕ ЗАПИСИ
# ════════════════════════════════════════════════════════════════════════════

@router.message(F.text == "🗑 Удалить запись")
async def delete_expense_start(message: Message, state: FSMContext):
    records = sheets.get_last_n_rows(5)
    if not records:
        await message.answer("📭 Нет записей для удаления.")
        await go_main(message, state)
        return

    # Сохраняем записи в состояние
    await state.update_data(delete_records=records)
    await state.set_state(DeleteExpense.waiting_choice)

    text = "🗑 <b>Выберите запись для удаления:</b>\n\n" + format_records(records)
    await message.answer(
        text,
        reply_markup=delete_records_kb(records),
        parse_mode="HTML",
    )


@router.message(DeleteExpense.waiting_choice)
async def delete_expense_choice(message: Message, state: FSMContext):
    text = message.text.strip()

    # Парсим номер из кнопки вида "🗑 Удалить 3"
    if not text.startswith("🗑 Удалить "):
        await message.answer("Нажмите одну из кнопок ниже или «❌ Отмена».")
        return

    try:
        choice = int(text.replace("🗑 Удалить ", ""))
    except ValueError:
        await message.answer("Неверный выбор.")
        return

    data = await state.get_data()
    records = data.get("delete_records", [])

    if choice < 1 or choice > len(records):
        await message.answer("Неверный номер записи.")
        return

    record = records[choice - 1]
    success = sheets.delete_row(record["sheet_row"])

    if success:
        await message.answer(
            f"✅ <b>Запись удалена:</b>\n"
            f"📌 {record['description']} — {record['amount']} ₸",
            parse_mode="HTML",
        )
    else:
        await message.answer("❌ Ошибка при удалении. Попробуйте ещё раз.")

    await go_main(message, state)


# ════════════════════════════════════════════════════════════════════════════
#  НАСТРОЙКИ АДМИНИСТРАТОРА
# ════════════════════════════════════════════════════════════════════════════

@router.message(F.text == "⚙️ Настройки")
async def admin_settings_menu(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к настройкам.")
        return

    week = admin_settings.get_week()
    month = admin_settings.get_month()
    await message.answer(
        f"⚙️ <b>Настройки</b>\n\n"
        f"📅 Текущая неделя: <b>{week}</b>\n"
        f"🗓 Текущий месяц: <b>{month}</b>",
        reply_markup=settings_menu(),
        parse_mode="HTML",
    )


# ── Изменить неделю ───────────────────────────────────────────────────────────

@router.message(F.text == "📅 Изменить неделю")
async def change_week_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа.")
        return
    await state.set_state(AdminSettings.waiting_week)
    await message.answer(
        "Введите номер недели (1–53):",
        reply_markup=cancel_kb(),
    )


@router.message(AdminSettings.waiting_week)
async def change_week_set(message: Message, state: FSMContext):
    try:
        week = int(message.text.strip())
        if not 1 <= week <= 53:
            raise ValueError
    except ValueError:
        await message.answer("⚠️ Введите число от 1 до 53:")
        return

    admin_settings.set_week(week)
    await message.answer(f"✅ Неделя изменена на <b>{week}</b>.", parse_mode="HTML")
    await go_main(message, state)


# ── Изменить месяц ────────────────────────────────────────────────────────────

@router.message(F.text == "🗓 Изменить месяц")
async def change_month_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа.")
        return
    await state.set_state(AdminSettings.waiting_month)
    await message.answer(
        "Выберите месяц:",
        reply_markup=months_kb(),
    )


VALID_MONTHS = {
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
}


@router.message(AdminSettings.waiting_month)
async def change_month_set(message: Message, state: FSMContext):
    month = message.text.strip()
    if month not in VALID_MONTHS:
        await message.answer("⚠️ Выберите месяц из кнопок ниже:")
        return

    admin_settings.set_month(month)
    await message.answer(f"✅ Месяц изменён на <b>{month}</b>.", parse_mode="HTML")
    await go_main(message, state)
