# 🤖 Telegram-бот для учёта затрат с Google Sheets

## Структура проекта

```
tg_expense_bot/
├── bot.py              — точка входа
├── config.py           — ВАШ ТОКЕН и настройки
├── handlers.py         — вся логика бота
├── sheets.py           — работа с Google Sheets
├── admin_settings.py   — хранение текущей недели/месяца
├── keyboards.py        — клавиатуры
├── states.py           — FSM-состояния
├── requirements.txt    — зависимости
└── service_account.json  — (создаёте сами, см. ниже)
```

---

## Шаг 1 — Получить токен Telegram-бота

1. Откройте Telegram, найдите **@BotFather**
2. Отправьте `/newbot` и следуйте инструкциям
3. Скопируйте полученный токен вида `7123456789:AAH...`
4. Вставьте его в `config.py`:
   ```python
   BOT_TOKEN = "7123456789:AAH..."
   ```

---

## Шаг 2 — Узнать свой Telegram user_id (для прав администратора)

1. Откройте **@userinfobot** в Telegram
2. Отправьте любое сообщение
3. Скопируйте число из поля `Id`
4. Вставьте в `config.py`:
   ```python
   ADMIN_ID = 123456789
   ```

---

## Шаг 3 — Создать Google Sheets таблицу

1. Откройте https://sheets.google.com
2. Создайте новую таблицу
3. Скопируйте ID из URL:
   ```
   https://docs.google.com/spreadsheets/d/  ВОТ_ЭТО_КОПИРУЕМ  /edit
   ```
4. Вставьте в `config.py`:
   ```python
   SPREADSHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"
   ```
5. Убедитесь, что название первого листа совпадает с `SHEET_NAME` (по умолчанию `"Лист1"`).
   Если лист называется иначе — поменяйте в `config.py`.

---

## Шаг 4 — Настроить Service Account (Google Cloud)

### 4.1 Создать проект

1. Откройте https://console.cloud.google.com
2. Нажмите **"Выбрать проект"** → **"Новый проект"**
3. Дайте любое название, нажмите **"Создать"**

### 4.2 Включить Google Sheets API

1. В меню слева: **API и сервисы → Библиотека**
2. Найдите **"Google Sheets API"**
3. Нажмите **"Включить"**

### 4.3 Создать Service Account

1. **API и сервисы → Учётные данные**
2. **"Создать учётные данные" → "Сервисный аккаунт"**
3. Введите любое имя, нажмите **"Создать и продолжить"**
4. Роль — **"Редактор"**, нажмите **"Продолжить"** → **"Готово"**

### 4.4 Скачать ключ (JSON)

1. В списке сервисных аккаунтов кликните на созданный аккаунт
2. Вкладка **"Ключи"** → **"Добавить ключ" → "Создать новый ключ"**
3. Формат — **JSON**, нажмите **"Создать"**
4. Файл скачается автоматически
5. Переименуйте его в `service_account.json`
6. Положите рядом с `bot.py`

### 4.5 Открыть доступ к таблице

1. Откройте скачанный JSON, найдите поле `"client_email"`:
   ```json
   "client_email": "your-bot@project-id.iam.gserviceaccount.com"
   ```
2. Откройте вашу Google Таблицу
3. Нажмите **"Настройки доступа"** (кнопка "Поделиться")
4. Добавьте этот email с правами **"Редактор"**
5. Нажмите **"Отправить"**

---

## Шаг 5 — Добавить пользователей

В `config.py` заполните словарь:

```python
USER_NAMES = {
    123456789: "Иван",       # admin
    987654321: "Мария",
    111222333: "Алексей",
}
```

Если user_id не найден — бот использует имя из Telegram-профиля.

---

## Шаг 6 — Установить зависимости и запустить

```bash
# Создать виртуальное окружение (рекомендуется)
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# Установить пакеты
pip install -r requirements.txt

# Запустить бота
python bot.py
```

---

## Структура таблицы Google Sheets

Бот автоматически создаст заголовки при первом запуске:

| Затраты на неделю | Сумма затрат | Дата       | Пользователь | Номер недели | Месяц   |
|-------------------|--------------|------------|--------------|--------------|---------|
| Продукты          | 5000         | 20.04.2025 | Иван         | 17           | Апрель  |

---

## Возможности бота

| Кнопка              | Что делает                                          |
|---------------------|-----------------------------------------------------|
| ➕ Добавить затрату  | Диалог: описание → сумма → запись в таблицу         |
| 📋 Последние траты   | Показывает 5 последних записей                      |
| 🗑 Удалить запись    | Показывает 5 записей с кнопками удаления            |
| ⚙️ Настройки        | Только для администратора: изменить неделю/месяц    |
| ❌ Отмена            | В любой момент возврат в главное меню               |

---

## Автозапуск через systemd (Linux/VPS)

Создайте файл `/etc/systemd/system/expense_bot.service`:

```ini
[Unit]
Description=Expense Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/tg_expense_bot
ExecStart=/home/ubuntu/tg_expense_bot/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable expense_bot
sudo systemctl start expense_bot
sudo systemctl status expense_bot
```
