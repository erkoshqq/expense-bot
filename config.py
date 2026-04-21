import os
import json

# ============================================================
#  Настройки берутся из переменных окружения (для Render/VPS)
#  При локальном запуске можно задать значения прямо здесь
# ============================================================

# Токен Telegram-бота — задаётся через env var BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# ID администраторов — можно указать несколько через запятую
# Локально: просто добавьте нужные ID в список ниже
# На Render: задайте env var ADMIN_IDS = "123456789,987654321"
_admin_ids_str = os.getenv("ADMIN_IDS", "")
if _admin_ids_str:
    ADMIN_IDS = {int(x.strip()) for x in _admin_ids_str.split(",") if x.strip()}
else:
    ADMIN_IDS = {
        123456789,   # Иван
        # 987654321, # Раскомментируйте для второго админа
    }

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
