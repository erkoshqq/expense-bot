"""
Хранилище настроек администратора (текущая неделя и месяц).
Данные сохраняются в файл settings.json между перезапусками бота.
"""
import json
import os
from datetime import datetime

SETTINGS_FILE = "settings.json"

_defaults = {
    "week_number": datetime.now().isocalendar()[1],
    "month": datetime.now().strftime("%B"),  # Название месяца на английском
}

# Русские названия месяцев
MONTHS_RU = {
    "January": "Январь", "February": "Февраль", "March": "Март",
    "April": "Апрель", "May": "Май", "June": "Июнь",
    "July": "Июль", "August": "Август", "September": "Сентябрь",
    "October": "Октябрь", "November": "Ноябрь", "December": "Декабрь",
}

MONTHS_LIST = list(MONTHS_RU.values())


def _load() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return _defaults.copy()


def _save(data: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_week() -> int:
    return _load().get("week_number", _defaults["week_number"])


def get_month() -> str:
    return _load().get("month", _defaults["month"])


def set_week(week: int):
    data = _load()
    data["week_number"] = week
    _save(data)


def set_month(month: str):
    data = _load()
    data["month"] = month
    _save(data)
