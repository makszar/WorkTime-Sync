from __future__ import annotations

import csv
import json
import os
import re
import uuid
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

DATASET_ORDER = ["employees", "events", "hr_profiles", "absences"]
ALLOWED_DATASETS = set(DATASET_ORDER)
ALLOWED_SUFFIXES = {".json", ".csv"}

REQUIRED_COLUMNS: dict[str, list[str]] = {
    "employees": [
        "id",
        "name",
        "team",
        "role",
        "timezone",
        "work_start",
        "work_end",
        "work_days",
        "work_format",
        "last_update_date",
    ],
    "events": [
        "id",
        "employee_id",
        "title",
        "start_datetime",
        "end_datetime",
        "source",
        "type",
    ],
    "hr_profiles": [
        "employee_id",
        "hr_timezone",
        "hr_work_format",
        "hr_work_start",
        "hr_work_end",
    ],
    "absences": [
        "id",
        "employee_id",
        "type",
        "start_date",
        "end_date",
    ],
}

MODEL_BY_DATASET: dict[str, Type[BaseModel]] = {
    "employees": Employee,
    "events": Event,
    "hr_profiles": HRProfile,
    "absences": Absence,
}


def _display_path(path: Path | None) -> str | None:
    if path is None:
        return None

    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve())


def _target_data_dir() -> Path:
    """Return the directory where uploads should be saved."""
    return Path(os.getenv("WORKTIME_DATA_DIR", DATA_DIR)).resolve()


def _normalize_identifier(value: Any) -> int:
    """Convert ids like emp001/evt001/abs001 to backend numeric ids."""
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
    """Keep datetime strings timezone-neutral for current analytics calculations."""
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
    """Convert simple CSV values to Python values."""
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


def _validate_columns(dataset: str, rows: list[dict[str, Any]], filename: str) -> None:
    """Validate required CSV/JSON columns before Pydantic row validation."""
    if not rows:
        return

    required = set(REQUIRED_COLUMNS.get(dataset, []))
    if not required:
        return

    present = set(rows[0].keys())
    missing = sorted(required - present)
    if missing:
        raise ValueError(f"В {filename} отсутствуют обязательные колонки: {', '.join(missing)}")


def _validate_rows(dataset: str, rows: List[Dict[str, Any]], filename: str = "") -> List[Dict[str, Any]]:
    """Validate loaded rows through Pydantic models."""
    model = MODEL_BY_DATASET.get(dataset)
    if not model:
        return rows

    _validate_columns(dataset, rows, filename or dataset)

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
    """Return data directories in priority order."""
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
        return _validate_rows(validate_as, rows, path.name) if validate_as else rows

    if required:
        tried = ", ".join(str(Path(directory) / filename) for directory in search_dirs)
        raise FileNotFoundError(f"Файл не найден. Проверенные пути: {tried}")

    return []


def _dataset_path_in_dir(dataset: str, directory: Path) -> Path | None:
    csv_path = Path(directory) / f"{dataset}.csv"
    json_path = Path(directory) / f"{dataset}.json"

    if csv_path.exists():
        return csv_path
    if json_path.exists():
        return json_path
    return None


def get_dataset_path(dataset: str) -> Path | None:
    """Return the actual file path used for a dataset, respecting priority."""
    for directory in _active_data_dirs():
        path = _dataset_path_in_dir(dataset, Path(directory))
        if path:
            return path
    return None


def get_data_source_info() -> dict[str, Any]:
    """Return current data source diagnostics for API/debug endpoints."""
    datasets = {dataset: get_dataset_path(dataset) for dataset in DATASET_ORDER}
    active_paths = [path for path in datasets.values() if path is not None]
    active_source = active_paths[0].parent if active_paths else _active_data_dirs()[0]

    return {
        "active_source": _display_path(active_source),
        "fallback_source": _display_path(FALLBACK_DATA_DIR),
        "env_override": bool(os.getenv("WORKTIME_DATA_DIR")),
        "priority": [_display_path(directory) for directory in _active_data_dirs()],
        "datasets": {dataset: _display_path(path) for dataset, path in datasets.items()},
    }


def get_schema_definitions() -> dict[str, list[str]]:
    """Return expected backend-ready dataset schemas."""
    return REQUIRED_COLUMNS


def load_dataset(dataset: str, required: bool = True) -> List[Dict[str, Any]]:
    """Load a dataset and prefer CSV over JSON inside the active data folder."""
    for directory in _active_data_dirs():
        path = _dataset_path_in_dir(dataset, Path(directory))
        if path:
            return load_table(path.name, required=required, validate_as=dataset, data_dir=Path(directory))

    if required:
        searched = []
        for directory in _active_data_dirs():
            searched.append(str(Path(directory) / f"{dataset}.csv"))
            searched.append(str(Path(directory) / f"{dataset}.json"))
        raise FileNotFoundError("Файл не найден. Проверенные пути: " + ", ".join(searched))

    return []


def save_uploaded_table(dataset: str, suffix: str, content: bytes) -> Path:
    """Safely save uploaded JSON/CSV into the main root data/synthetic folder.

    The previous working dataset remains untouched if validation fails.
    """
    if dataset not in ALLOWED_DATASETS:
        raise ValueError("Неизвестный набор данных")
    if suffix not in ALLOWED_SUFFIXES:
        raise ValueError("Можно загружать только JSON или CSV")

    target_dir = _target_data_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    final_path = target_dir / f"{dataset}{suffix}"
    temp_path = target_dir / f".{dataset}.upload-{uuid.uuid4().hex}{suffix}"

    temp_path.write_bytes(content)

    try:
        load_table(temp_path.name, validate_as=dataset, data_dir=target_dir)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    temp_path.replace(final_path)

    # Keep only one active uploaded source for the dataset in data/synthetic.
    alternate_suffix = ".json" if suffix == ".csv" else ".csv"
    alternate_path = target_dir / f"{dataset}{alternate_suffix}"
    if alternate_path.exists():
        alternate_path.unlink()

    return final_path


def load_employees() -> List[Dict[str, Any]]:
    return load_dataset("employees")


def load_events() -> List[Dict[str, Any]]:
    return load_dataset("events")


def load_hr_profiles() -> List[Dict[str, Any]]:
    return load_dataset("hr_profiles")


def load_absences() -> List[Dict[str, Any]]:
    return load_dataset("absences", required=False)
