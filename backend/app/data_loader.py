from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Type

from pydantic import BaseModel, ValidationError

from app.models import Absence, Employee, Event, HRProfile

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

MODEL_BY_DATASET: dict[str, Type[BaseModel]] = {
    "employees": Employee,
    "events": Event,
    "hr_profiles": HRProfile,
    "absences": Absence,
}


def _convert_csv_value(value: str | None) -> Any:
    """Convert simple CSV values to Python values.

    Semicolon-separated cells are used for arrays, for example:
    work_days = "Mon;Tue;Wed;Thu;Fri".
    """
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


def _validate_rows(dataset: str, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate loaded rows through Pydantic models.

    This catches broken JSON/CSV early and gives a readable error instead of a
    random 500 during analytics calculations.
    """
    model = MODEL_BY_DATASET.get(dataset)
    if not model:
        return rows

    validated: List[Dict[str, Any]] = []
    errors: list[str] = []

    for index, row in enumerate(rows, start=1):
        try:
            validated.append(model(**row).model_dump())
        except ValidationError as error:
            errors.append(f"row {index}: {error.errors()}")

    if errors:
        joined = "; ".join(errors[:3])
        raise ValueError(f"Некорректные данные в {dataset}: {joined}")

    return validated


def load_table(filename: str, required: bool = True, validate_as: str | None = None) -> List[Dict[str, Any]]:
    """Read a table from JSON or CSV and optionally validate it.

    JSON is convenient for nested values, CSV is convenient for quick imports
    from spreadsheet tools. CSV cells with `;` are converted into arrays.
    """
    path = DATA_DIR / filename

    if not path.exists():
        if required:
            raise FileNotFoundError(f"Файл не найден: {path}")
        return []

    if path.suffix == ".json":
        with path.open("r", encoding="utf-8") as file:
            rows = json.load(file)
    elif path.suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            rows = [
                {key: _convert_csv_value(value) for key, value in row.items()}
                for row in reader
            ]
    else:
        raise ValueError("Поддерживаются только .json и .csv файлы")

    if not isinstance(rows, list):
        raise ValueError(f"Файл {filename} должен содержать список объектов")

    return _validate_rows(validate_as, rows) if validate_as else rows


def load_dataset(dataset: str, required: bool = True) -> List[Dict[str, Any]]:
    """Load a dataset and prefer uploaded CSV over default JSON.

    If `employees.csv` was uploaded, it will be used instead of `employees.json`.
    This makes POST /upload/{dataset} meaningful for both JSON and CSV files.
    """
    csv_path = DATA_DIR / f"{dataset}.csv"
    json_path = DATA_DIR / f"{dataset}.json"

    if csv_path.exists():
        return load_table(f"{dataset}.csv", required=required, validate_as=dataset)

    if json_path.exists():
        return load_table(f"{dataset}.json", required=required, validate_as=dataset)

    if required:
        raise FileNotFoundError(f"Файл не найден: {json_path} или {csv_path}")

    return []


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

    try:
        load_table(path.name, validate_as=dataset)
    except Exception:
        path.unlink(missing_ok=True)
        raise

    # Keep only one active uploaded source for the dataset. If a CSV is uploaded,
    # remove JSON and vice versa, so the loader cannot accidentally read stale data.
    alternate_suffix = ".json" if suffix == ".csv" else ".csv"
    alternate_path = DATA_DIR / f"{dataset}{alternate_suffix}"
    if alternate_path.exists():
        alternate_path.unlink()

    return path


def load_employees() -> List[Dict[str, Any]]:
    return load_dataset("employees")


def load_events() -> List[Dict[str, Any]]:
    return load_dataset("events")


def load_hr_profiles() -> List[Dict[str, Any]]:
    return load_dataset("hr_profiles")


def load_absences() -> List[Dict[str, Any]]:
    return load_dataset("absences", required=False)
