from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# ── Главное меню (обычный пользователь) ──────────────────────────────────────
def main_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="➕ Добавить затрату")],
        [KeyboardButton(text="📋 Последние траты")],
        [KeyboardButton(text="🗑 Удалить запись")],
    ]
    if is_admin:
        buttons.append([KeyboardButton(text="⚙️ Настройки")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# ── Кнопка отмены ────────────────────────────────────────────────────────────
def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )


# ── Меню настроек (только для админа) ────────────────────────────────────────
def settings_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Изменить неделю")],
            [KeyboardButton(text="🗓 Изменить месяц")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


# ── Инлайн-подобные кнопки удаления (через Reply) ────────────────────────────
def delete_records_kb(records: list) -> ReplyKeyboardMarkup:
    """Кнопки 'Удалить 1' … 'Удалить N' под каждой записью + Отмена."""
    buttons = [[KeyboardButton(text=f"🗑 Удалить {i + 1}")] for i in range(len(records))]
    buttons.append([KeyboardButton(text="❌ Отмена")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# ── Список месяцев ────────────────────────────────────────────────────────────
def months_kb() -> ReplyKeyboardMarkup:
    months = [
        ["Январь", "Февраль", "Март"],
        ["Апрель", "Май", "Июнь"],
        ["Июль", "Август", "Сентябрь"],
        ["Октябрь", "Ноябрь", "Декабрь"],
        ["❌ Отмена"],
    ]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=m) for m in row] for row in months],
        resize_keyboard=True,
    )


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
