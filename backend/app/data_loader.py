from __future__ import annotations

import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Type

from pydantic import BaseModel, ValidationError

from app.models import Absence, Employee, Event, HRProfile

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

# Main team data folder. Backend reads normalized demo data from repo-root data/synthetic.
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "synthetic"

# Temporary fallback for backward compatibility while the team migrates data.
FALLBACK_DATA_DIR = BACKEND_DIR / "data"

# Optional override for local experiments:
# PowerShell: $env:WORKTIME_DATA_DIR="C:\path\to\WorkTime-Sync\data\synthetic"
DATA_DIR = Path(os.getenv("WORKTIME_DATA_DIR", DEFAULT_DATA_DIR)).resolve()

MODEL_BY_DATASET: dict[str, Type[BaseModel]] = {
    "employees": Employee,
    "events": Event,
    "hr_profiles": HRProfile,
    "absences": Absence,
}


def _normalize_identifier(value: Any) -> int:
    """Convert ids like emp001/evt001/abs001 to backend numeric ids.

    The analytics layer currently works with integer ids, while the shared
    `data/synthetic` CSV files use human-readable string ids.
    """
    if isinstance(value, int):
        return value

    text = str(value).strip()
    if text.isdigit():
        return int(text)

    match = re.search(r"(\d+)$", text)
    if match:
        return int(match.group(1))

    raise ValueError(f"Некорректный идентификатор: {value}")


def _normalize_datetime(value: Any) -> Any:
    """Keep datetime strings timezone-neutral for current analytics calculations.

    Source CSV may contain ISO datetimes with offsets, for example
    2026-05-20T10:00:00+03:00. Current availability calculations compare these
    values with timezone-neutral demo-week slots, so we preserve the local clock
    time and remove tzinfo.
    """
    if not isinstance(value, str):
        return value

    text = value.strip()
    if "T" not in text:
        return value

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return value

    return parsed.replace(tzinfo=None).isoformat(timespec="seconds")


def _convert_csv_value(value: str | None) -> Any:
    """Convert simple CSV values to Python values.

    Supported list delimiters for `work_days`:
    - Mon;Tue;Wed
    - Mon|Tue|Wed
    """
    if value is None:
        return value

    text = value.strip()
    if not text:
        return text

    if ";" in text:
        return [item.strip() for item in text.split(";") if item.strip()]

    if "|" in text:
        return [item.strip() for item in text.split("|") if item.strip()]

    if text.isdigit():
        return int(text)

    return text


def _normalize_row(dataset: str, row: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize shared CSV/JSON data into the backend-ready schema."""
    normalized = dict(row)

    if dataset == "employees":
        normalized["id"] = _normalize_identifier(normalized["id"])

        # Some CSV files use a single string for work_days.
        if isinstance(normalized.get("work_days"), str):
            normalized["work_days"] = _convert_csv_value(normalized["work_days"])

    elif dataset == "events":
        normalized["id"] = _normalize_identifier(normalized["id"])
        normalized["employee_id"] = _normalize_identifier(normalized["employee_id"])
        normalized["start_datetime"] = _normalize_datetime(normalized["start_datetime"])
        normalized["end_datetime"] = _normalize_datetime(normalized["end_datetime"])

    elif dataset == "hr_profiles":
        normalized["employee_id"] = _normalize_identifier(normalized["employee_id"])

    elif dataset == "absences":
        normalized["id"] = _normalize_identifier(normalized["id"])
        normalized["employee_id"] = _normalize_identifier(normalized["employee_id"])

    return normalized


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
            normalized = _normalize_row(dataset, row)
            validated.append(model(**normalized).model_dump())
        except (ValidationError, ValueError, KeyError) as error:
            if isinstance(error, ValidationError):
                details = error.errors()
            else:
                details = str(error)
            errors.append(f"row {index}: {details}")

    if errors:
        joined = "; ".join(errors[:3])
        raise ValueError(f"Некорректные данные в {dataset}: {joined}")

    return validated


def _active_data_dirs() -> list[Path]:
    """Return data directories in priority order.

    Priority:
    1. WORKTIME_DATA_DIR, if explicitly provided.
    2. repo-root data/synthetic.
    3. backend/data as temporary fallback.
    """
    env_value = os.getenv("WORKTIME_DATA_DIR")
    if env_value:
        return [Path(env_value).resolve()]

    dirs = [DATA_DIR]
    fallback = FALLBACK_DATA_DIR.resolve()
    if fallback not in dirs:
        dirs.append(fallback)
    return dirs


def _read_table(path: Path) -> List[Dict[str, Any]]:
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
        raise ValueError(f"Файл {path.name} должен содержать список объектов")

    return rows


def load_table(
    filename: str,
    required: bool = True,
    validate_as: str | None = None,
    data_dir: Path | None = None,
) -> List[Dict[str, Any]]:
    """Read a table from JSON or CSV and optionally validate it."""
    search_dirs = [data_dir] if data_dir else _active_data_dirs()

    for directory in search_dirs:
        path = Path(directory) / filename
        if not path.exists():
            continue

        rows = _read_table(path)
        return _validate_rows(validate_as, rows) if validate_as else rows

    if required:
        tried = ", ".join(str(Path(directory) / filename) for directory in search_dirs)
        raise FileNotFoundError(f"Файл не найден. Проверенные пути: {tried}")

    return []


def load_dataset(dataset: str, required: bool = True) -> List[Dict[str, Any]]:
    """Load a dataset and prefer CSV over JSON inside the active data folder.

    Backend-ready datasets should live in repo-root `data/synthetic`.
    Expected files:
    - employees.json/csv
    - events.json/csv
    - hr_profiles.json/csv
    - absences.json/csv
    """
    for directory in _active_data_dirs():
        csv_path = Path(directory) / f"{dataset}.csv"
        json_path = Path(directory) / f"{dataset}.json"

        if csv_path.exists():
            return load_table(f"{dataset}.csv", required=required, validate_as=dataset, data_dir=Path(directory))

        if json_path.exists():
            return load_table(f"{dataset}.json", required=required, validate_as=dataset, data_dir=Path(directory))

    if required:
        searched = []
        for directory in _active_data_dirs():
            searched.append(str(Path(directory) / f"{dataset}.csv"))
            searched.append(str(Path(directory) / f"{dataset}.json"))
        raise FileNotFoundError("Файл не найден. Проверенные пути: " + ", ".join(searched))

    return []


def save_uploaded_table(dataset: str, suffix: str, content: bytes) -> Path:
    """Save uploaded JSON/CSV into the main root data/synthetic folder.

    Upload is intentionally saved to the shared team data folder, not backend/data,
    so future API calls and team edits use the same source of truth.
    """
    allowed_datasets = {"employees", "events", "hr_profiles", "absences"}
    allowed_suffixes = {".json", ".csv"}

    if dataset not in allowed_datasets:
        raise ValueError("Неизвестный набор данных")
    if suffix not in allowed_suffixes:
        raise ValueError("Можно загружать только JSON или CSV")

    target_dir = DATA_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    path = target_dir / f"{dataset}{suffix}"
    path.write_bytes(content)

    try:
        load_table(path.name, validate_as=dataset, data_dir=target_dir)
    except Exception:
        path.unlink(missing_ok=True)
        raise

    # Keep only one active uploaded source for the dataset in data/synthetic.
    alternate_suffix = ".json" if suffix == ".csv" else ".csv"
    alternate_path = target_dir / f"{dataset}{alternate_suffix}"
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
