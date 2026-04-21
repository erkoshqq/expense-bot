import os
import json

# ============================================================
#  Настройки берутся из переменных окружения (для Render/VPS)
#  При локальном запуске можно задать значения прямо здесь
# ============================================================

# Токен Telegram-бота — задаётся через env var BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# ID администратора — задаётся через env var ADMIN_ID
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

# Словарь: Telegram user_id → имя пользователя
# При деплое на Render задайте через env var USER_NAMES_JSON
# Формат JSON: '{"123456789": "Иван", "987654321": "Мария"}'
_user_names_json = os.getenv("USER_NAMES_JSON", "")
if _user_names_json:
    USER_NAMES = {int(k): v for k, v in json.loads(_user_names_json).items()}
else:
    # Редактируйте этот словарь при локальном запуске
    USER_NAMES = {
        123456789: "Иван",
        987654321: "Мария",
        111222333: "Алексей",
    }

# ID таблицы Google Sheets — задаётся через env var SPREADSHEET_ID
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "YOUR_SPREADSHEET_ID")

# Название листа в таблице
SHEET_NAME = os.getenv("SHEET_NAME", "Лист1")

# ── Service Account ──────────────────────────────────────────────────────────
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")

# Если задана env var SERVICE_ACCOUNT_JSON — создаём файл автоматически.
# Так не нужно загружать файл на Render вручную.
_sa_json = os.getenv("SERVICE_ACCOUNT_JSON", "")
if _sa_json:
    with open(SERVICE_ACCOUNT_FILE, "w") as _f:
        _f.write(_sa_json)
