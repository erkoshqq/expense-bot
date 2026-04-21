import logging
from datetime import datetime
from typing import Optional

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import SERVICE_ACCOUNT_FILE, SPREADSHEET_ID, SHEET_NAME

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Заголовки колонок в таблице
HEADERS = [
    "Затраты на неделю",
    "Сумма затрат",
    "Дата",
    "Пользователь",
    "Номер недели",
    "Месяц",
]


def get_service():
    """Создаёт и возвращает клиент Google Sheets API."""
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets()


def ensure_headers():
    """Проверяет наличие заголовков в таблице и создаёт их при необходимости."""
    try:
        sheet = get_service()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A1:F1"
        ).execute()
        values = result.get("values", [])
        if not values or values[0] != HEADERS:
            sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEET_NAME}!A1:F1",
                valueInputOption="RAW",
                body={"values": [HEADERS]}
            ).execute()
            logger.info("Заголовки таблицы созданы")
    except HttpError as e:
        logger.error(f"Ошибка при проверке заголовков: {e}")


def append_expense(description: str, amount: float, user_name: str,
                   week_number: int, month: str) -> bool:
    """Добавляет новую запись о затрате в таблицу."""
    try:
        sheet = get_service()
        date_str = datetime.now().strftime("%d.%m.%Y")
        row = [description, amount, date_str, user_name, week_number, month]
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:F",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]}
        ).execute()
        logger.info(f"Добавлена запись: {description} — {amount}")
        return True
    except HttpError as e:
        logger.error(f"Ошибка при добавлении записи: {e}")
        return False


def get_all_rows() -> list[list]:
    """Возвращает все строки данных (без заголовка)."""
    try:
        sheet = get_service()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:F"
        ).execute()
        rows = result.get("values", [])
        # Пропускаем заголовок (первая строка)
        if rows and rows[0] == HEADERS:
            return rows[1:]
        return rows
    except HttpError as e:
        logger.error(f"Ошибка при получении данных: {e}")
        return []


def get_last_n_rows(n: int = 5) -> list[dict]:
    """Возвращает последние n записей с их реальными индексами строк."""
    rows = get_all_rows()
    last_rows = rows[-n:] if len(rows) >= n else rows
    result = []
    for i, row in enumerate(last_rows):
        # sheet_row_index — номер строки в таблице (1-based, +1 за заголовок)
        sheet_index = len(rows) - len(last_rows) + i + 2  # +2: заголовок + 1-based
        result.append({
            "sheet_row": sheet_index,
            "description": row[0] if len(row) > 0 else "",
            "amount": row[1] if len(row) > 1 else "",
            "date": row[2] if len(row) > 2 else "",
            "user": row[3] if len(row) > 3 else "",
            "week": row[4] if len(row) > 4 else "",
            "month": row[5] if len(row) > 5 else "",
        })
    return result


def delete_row(sheet_row_index: int) -> bool:
    """Удаляет строку по её номеру в таблице (1-based)."""
    try:
        sheet = get_service()
        # Получаем sheetId листа
        spreadsheet = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_id = None
        for s in spreadsheet["sheets"]:
            if s["properties"]["title"] == SHEET_NAME:
                sheet_id = s["properties"]["sheetId"]
                break
        if sheet_id is None:
            logger.error("Лист не найден")
            return False

        # deleteDimension использует 0-based индексы
        body = {
            "requests": [{
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": sheet_row_index - 1,  # 0-based
                        "endIndex": sheet_row_index          # exclusive
                    }
                }
            }]
        }
        sheet.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        logger.info(f"Удалена строка {sheet_row_index}")
        return True
    except HttpError as e:
        logger.error(f"Ошибка при удалении строки: {e}")
        return False
