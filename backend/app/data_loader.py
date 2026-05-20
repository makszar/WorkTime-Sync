from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def _convert_csv_value(value: str) -> Any:
    if value is None:
        return value
    text = value.strip()
    if not text:
        return text
    if ";" in text:
        return [item.strip() for item in text.split(";") if item.strip()]
    if text.isdigit():
        return int(text)
    return text


def load_table(filename: str, required: bool = True) -> List[Dict[str, Any]]:
    """Читает таблицу из JSON или CSV.

    Для MVP данные хранятся в файлах. JSON удобен для массивов, CSV — для быстрой
    загрузки из таблиц. CSV-значения с `;` превращаются в список.
    """
    path = DATA_DIR / filename

    if not path.exists():
        if required:
            raise FileNotFoundError(f"Файл не найден: {path}")
        return []

    if path.suffix == ".json":
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    if path.suffix == ".csv":
        with path.open("r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return [
                {key: _convert_csv_value(value) for key, value in row.items()}
                for row in reader
            ]

    raise ValueError("Поддерживаются только .json и .csv файлы")


def save_uploaded_table(dataset: str, suffix: str, content: bytes) -> Path:
    allowed_datasets = {"employees", "events", "hr_profiles", "absences"}
    allowed_suffixes = {".json", ".csv"}

    if dataset not in allowed_datasets:
        raise ValueError("Неизвестный набор данных")
    if suffix not in allowed_suffixes:
        raise ValueError("Можно загружать только JSON или CSV")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{dataset}{suffix}"
    path.write_bytes(content)
    return path


def load_employees() -> List[Dict[str, Any]]:
    return load_table("employees.json")


def load_events() -> List[Dict[str, Any]]:
    return load_table("events.json")


def load_hr_profiles() -> List[Dict[str, Any]]:
    return load_table("hr_profiles.json")


def load_absences() -> List[Dict[str, Any]]:
    return load_table("absences.json", required=False)
