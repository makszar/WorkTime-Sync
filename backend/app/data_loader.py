import csv
import json
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_table(filename: str) -> List[Dict[str, Any]]:
    """Читает данные из JSON или CSV по расширению файла."""
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")

    if path.suffix == ".json":
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    if path.suffix == ".csv":
        with path.open("r", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    raise ValueError("Поддерживаются только .json и .csv файлы")


def load_employees() -> List[Dict[str, Any]]:
    return load_table("employees.json")


def load_events() -> List[Dict[str, Any]]:
    return load_table("events.json")


def load_hr_profiles() -> List[Dict[str, Any]]:
    return load_table("hr_profiles.json")
