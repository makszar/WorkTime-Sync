from __future__ import annotations

from collections import Counter
from datetime import date, datetime
from typing import Any, Dict, List


def _duplicates(values: list[int]) -> list[int]:
    counts = Counter(values)
    return sorted([value for value, count in counts.items() if count > 1])


def build_data_quality(
    employees: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    hr_profiles: List[Dict[str, Any]],
    absences: List[Dict[str, Any]],
    source_info: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    employee_ids = {int(employee["id"]) for employee in employees}
    event_ids = [int(event["id"]) for event in events]
    absence_ids = [int(absence["id"]) for absence in absences]
    hr_employee_ids = {int(profile["employee_id"]) for profile in hr_profiles}

    orphan_events = [
        {"event_id": int(event["id"]), "employee_id": int(event["employee_id"]), "title": event.get("title", "")}
        for event in events
        if int(event["employee_id"]) not in employee_ids
    ]
    orphan_absences = [
        {"absence_id": int(absence["id"]), "employee_id": int(absence["employee_id"]), "type": absence.get("type", "")}
        for absence in absences
        if int(absence["employee_id"]) not in employee_ids
    ]
    orphan_hr_profiles = [
        {"employee_id": int(profile["employee_id"])}
        for profile in hr_profiles
        if int(profile["employee_id"]) not in employee_ids
    ]
    employees_without_hr_profile = [
        {"employee_id": int(employee["id"]), "name": employee.get("name", ""), "team": employee.get("team", "")}
        for employee in employees
        if int(employee["id"]) not in hr_employee_ids
    ]

    invalid_event_ranges = []
    for event in events:
        try:
            start = datetime.fromisoformat(event["start_datetime"])
            end = datetime.fromisoformat(event["end_datetime"])
            if end <= start:
                invalid_event_ranges.append({"event_id": int(event["id"]), "title": event.get("title", ""), "reason": "end_datetime должен быть позже start_datetime"})
        except ValueError as error:
            invalid_event_ranges.append({"event_id": int(event["id"]), "title": event.get("title", ""), "reason": f"Некорректный datetime: {error}"})

    invalid_absence_ranges = []
    for absence in absences:
        try:
            start = date.fromisoformat(absence["start_date"])
            end = date.fromisoformat(absence["end_date"])
            if end < start:
                invalid_absence_ranges.append({"absence_id": int(absence["id"]), "employee_id": int(absence["employee_id"]), "reason": "end_date должен быть не раньше start_date"})
        except ValueError as error:
            invalid_absence_ranges.append({"absence_id": int(absence["id"]), "employee_id": int(absence["employee_id"]), "reason": f"Некорректная дата: {error}"})

    warnings = []
    if orphan_hr_profiles:
        warnings.append("Есть HR-профили для сотрудников, которых нет в employees.")
    if employees_without_hr_profile:
        warnings.append("Есть сотрудники без HR-профиля.")
    if len(hr_profiles) != len(employees):
        warnings.append("Количество HR-профилей отличается от количества сотрудников.")

    blocking_issues = (
        orphan_events or orphan_absences or invalid_event_ranges or invalid_absence_ranges
        or _duplicates([int(employee["id"]) for employee in employees])
        or _duplicates(event_ids) or _duplicates(absence_ids)
    )

    return {
        "status": "warning" if warnings and not blocking_issues else ("error" if blocking_issues else "ok"),
        "source": (source_info or {}).get("active_source"),
        "employees": len(employees),
        "events": len(events),
        "hr_profiles": len(hr_profiles),
        "absences": len(absences),
        "teams": sorted({employee.get("team", "") for employee in employees if employee.get("team")}),
        "duplicate_employee_ids": _duplicates([int(employee["id"]) for employee in employees]),
        "duplicate_event_ids": _duplicates(event_ids),
        "duplicate_absence_ids": _duplicates(absence_ids),
        "orphan_events": orphan_events,
        "orphan_absences": orphan_absences,
        "orphan_hr_profiles": orphan_hr_profiles,
        "employees_without_hr_profile": employees_without_hr_profile,
        "invalid_event_ranges": invalid_event_ranges,
        "invalid_absence_ranges": invalid_absence_ranges,
        "warnings": warnings,
        "datasets": (source_info or {}).get("datasets", {}),
    }