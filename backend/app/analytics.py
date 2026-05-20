from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional

MAX_DAYS_WITHOUT_UPDATE = 90
DEMO_TODAY = date(2026, 5, 19)
DEMO_WEEK_START = date(2026, 5, 18)  # Monday. Keeps demo calculations reproducible.

WEEKDAY_BY_INDEX = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun",
}

RU_WEEKDAY = {
    "Mon": "Пн",
    "Tue": "Вт",
    "Wed": "Ср",
    "Thu": "Чт",
    "Fri": "Пт",
    "Sat": "Сб",
    "Sun": "Вс",
}

DAY_INDEX_BY_RU = {value: index for index, value in enumerate(["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"])}
CODE_BY_RU = {value: key for key, value in RU_WEEKDAY.items()}

FORMAT_LABEL = {
    "remote": "Удаленно",
    "hybrid": "Гибрид",
    "office": "Офис",
}

TIMEZONE_LABEL = {
    "Europe/Moscow": "UTC+3",
    "Asia/Yekaterinburg": "UTC+5",
    "Asia/Samarkand": "UTC+5",
    "Asia/Dubai": "UTC+4",
}

PRIORITY_ORDER = {"Срочно": 0, "Важно": 1, "В работе": 2, "Планово": 3}


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def parse_time(value: str) -> time:
    return time.fromisoformat(value)


def clamp(value: float, minimum: float = 0, maximum: float = 1) -> float:
    return min(max(value, minimum), maximum)


def round2(value: float) -> float:
    return round(value, 2)


def percent(value: float) -> int:
    return round(clamp(value) * 100)


def weekday_code(dt: datetime) -> str:
    return WEEKDAY_BY_INDEX[dt.weekday()]


def weekday_label(dt: datetime) -> str:
    return RU_WEEKDAY[weekday_code(dt)]


def slot_date(day_label: str) -> date:
    return DEMO_WEEK_START + timedelta(days=DAY_INDEX_BY_RU[day_label])


def slot_interval(day_label: str, hour: int) -> tuple[datetime, datetime]:
    current_date = slot_date(day_label)
    start = datetime.combine(current_date, time(hour=hour))
    end = start + timedelta(hours=1)
    return start, end


def event_duration_hours(event: Dict[str, Any]) -> float:
    start = parse_datetime(event["start_datetime"])
    end = parse_datetime(event["end_datetime"])
    return max(0, (end - start).total_seconds() / 3600)


def daily_work_hours(employee: Dict[str, Any]) -> float:
    start = datetime.combine(DEMO_TODAY, parse_time(employee["work_start"]))
    end = datetime.combine(DEMO_TODAY, parse_time(employee["work_end"]))
    return max(0, (end - start).total_seconds() / 3600)


def weekly_work_hours(employee: Dict[str, Any]) -> float:
    return daily_work_hours(employee) * len(employee.get("work_days", []))


def employee_events(employee: Dict[str, Any], events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    employee_id = int(employee["id"])
    return [event for event in events if int(event["employee_id"]) == employee_id]


def employee_absences(employee: Dict[str, Any], absences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    employee_id = int(employee["id"])
    return [absence for absence in absences if int(absence["employee_id"]) == employee_id]


def intervals_overlap(start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> bool:
    return start_a < end_b and end_a > start_b


def is_event_outside_work_time(event: Dict[str, Any], employee: Dict[str, Any]) -> bool:
    start = parse_datetime(event["start_datetime"])
    end = parse_datetime(event["end_datetime"])

    if weekday_code(start) not in employee["work_days"]:
        return True

    work_start = parse_time(employee["work_start"])
    work_end = parse_time(employee["work_end"])

    return start.time() < work_start or end.time() > work_end


def is_absent_on_date(employee: Dict[str, Any], absences: List[Dict[str, Any]], current_date: date) -> Optional[Dict[str, Any]]:
    for absence in employee_absences(employee, absences):
        start = parse_date(absence["start_date"])
        end = parse_date(absence["end_date"])
        if start <= current_date <= end:
            return absence
    return None


def blocking_event_for_slot(
    employee: Dict[str, Any],
    events: List[Dict[str, Any]],
    day_label: str,
    hour: int,
) -> Optional[Dict[str, Any]]:
    slot_start, slot_end = slot_interval(day_label, hour)
    for event in employee_events(employee, events):
        event_start = parse_datetime(event["start_datetime"])
        event_end = parse_datetime(event["end_datetime"])
        if intervals_overlap(slot_start, slot_end, event_start, event_end):
            return event
    return None


def hr_flags(employee: Dict[str, Any], hr_profile: Optional[Dict[str, Any]]) -> Dict[str, int]:
    if not hr_profile:
        return {"timezone_mismatch": 0, "hr_mismatch": 0}

    timezone_mismatch = int(employee["timezone"] != hr_profile["hr_timezone"])
    hr_mismatch = int(
        employee["work_format"] != hr_profile["hr_work_format"]
        or employee["work_start"] != hr_profile["hr_work_start"]
        or employee["work_end"] != hr_profile["hr_work_end"]
    )
    return {"timezone_mismatch": timezone_mismatch, "hr_mismatch": hr_mismatch}


def risk_status(risk: float) -> str:
    if risk < 0.25:
        return "низкий"
    if risk < 0.50:
        return "средний"
    if risk < 0.75:
        return "высокий"
    return "критический"


def risk_tone(risk: float) -> str:
    if risk >= 0.75:
        return "critical"
    if risk >= 0.50:
        return "high"
    if risk >= 0.25:
        return "medium"
    return "low"


def calculate_employee_metrics(
    employee: Dict[str, Any],
    events: List[Dict[str, Any]],
    hr_profile: Optional[Dict[str, Any]],
    absences: Optional[List[Dict[str, Any]]] = None,
    today: date = DEMO_TODAY,
) -> Dict[str, Any]:
    absences = absences or []
    current_events = employee_events(employee, events)
    current_absences = employee_absences(employee, absences)

    days_since_update = max(0, (today - parse_date(employee["last_update_date"])).days)
    schedule_actuality = clamp(1 - days_since_update / MAX_DAYS_WITHOUT_UPDATE)

    outside_work_events = sum(
        1 for event in current_events if is_event_outside_work_time(event, employee)
    )
    total_events = len(current_events)
    outside_work_ratio = outside_work_events / total_events if total_events else 0

    busy_hours = sum(event_duration_hours(event) for event in current_events)
    work_hours = weekly_work_hours(employee)
    load = busy_hours / work_hours if work_hours else 0

    flags = hr_flags(employee, hr_profile)
    active_absence_count = len(current_absences)
    calendar_conflict_count = outside_work_events
    data_mismatch_count = flags["timezone_mismatch"] + flags["hr_mismatch"]
    issue_count = calendar_conflict_count + data_mismatch_count + active_absence_count

    risk = (
        0.30 * (1 - schedule_actuality)
        + 0.25 * outside_work_ratio
        + 0.25 * load
        + 0.10 * flags["timezone_mismatch"]
        + 0.10 * flags["hr_mismatch"]
    )
    risk = clamp(risk)

    return {
        "days_since_update": days_since_update,
        "schedule_actuality": round2(schedule_actuality),
        "outside_work_events": outside_work_events,
        "total_events": total_events,
        "outside_work_ratio": round2(outside_work_ratio),
        "busy_hours": round2(busy_hours),
        "work_hours": round2(work_hours),
        "load": round2(load),
        "timezone_mismatch": flags["timezone_mismatch"],
        "hr_mismatch": flags["hr_mismatch"],
        "absence_count": active_absence_count,
        "calendar_conflict_count": calendar_conflict_count,
        "data_mismatch_count": data_mismatch_count,
        "issue_count": issue_count,
        # Backward-compatible field for existing frontend/cards.
        "conflict_count": calendar_conflict_count,
        "risk": round2(risk),
        "risk_status": risk_status(risk),
        "risk_tone": risk_tone(risk),
    }


def build_recommendation_texts(employee: Dict[str, Any], metrics: Dict[str, Any]) -> List[str]:
    recommendations: List[str] = []

    if metrics["days_since_update"] > 60:
        recommendations.append("Обновить рабочий график: данные не актуализировались больше 60 дней.")
    if metrics["outside_work_ratio"] >= 0.3:
        recommendations.append("Проверить встречи вне рабочего времени и перенести регулярные события.")
    if metrics["load"] >= 0.8:
        recommendations.append("Проверить загрузку: календарь близок к перегрузке.")
    if metrics["timezone_mismatch"]:
        recommendations.append("Сверить часовой пояс сотрудника с HR-профилем.")
    if metrics["hr_mismatch"]:
        recommendations.append("Согласовать рабочий формат и часы с HR-данными.")
    if metrics.get("absence_count", 0):
        recommendations.append("Учесть временные исключения: отпуск, больничный или командировку.")
    if not recommendations:
        recommendations.append("Критичных проблем не найдено, график выглядит актуальным.")

    return recommendations


def build_status_note(metrics: Dict[str, Any]) -> str:
    if metrics["risk"] >= 0.75:
        return "Критический риск: график нужно подтвердить в первую очередь."
    if metrics["days_since_update"] > MAX_DAYS_WITHOUT_UPDATE:
        return "Данные не обновлялись больше 90 дней, график может быть устаревшим."
    if metrics["outside_work_events"] > 0:
        return "Есть встречи вне рабочего времени, стоит проверить календарь."
    if metrics["timezone_mismatch"] or metrics["hr_mismatch"]:
        return "Есть расхождение с HR-профилем, нужно сверить данные."
    if metrics["load"] >= 0.8:
        return "Высокая загрузка: новые встречи лучше не добавлять."
    return "График выглядит актуальным, критичных проблем не найдено."


def format_label(work_format: str) -> str:
    return FORMAT_LABEL.get(work_format, work_format)


def timezone_label(timezone: str) -> str:
    return TIMEZONE_LABEL.get(timezone, timezone)


def work_days_label(work_days: List[str]) -> List[str]:
    return [RU_WEEKDAY.get(day, day) for day in work_days]


def hour_int(value: str) -> int:
    return parse_time(value).hour


def to_frontend_employee(employee: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": int(employee["id"]),
        "name": employee["name"],
        "role": employee["role"],
        "team": employee["team"],
        "format": format_label(employee["work_format"]),
        "timezone": timezone_label(employee["timezone"]),
        "workDays": work_days_label(employee["work_days"]),
        "workStart": hour_int(employee["work_start"]),
        "workEnd": hour_int(employee["work_end"]),
        "updatedAt": employee["last_update_date"],
        "meetingsTotal": metrics["total_events"],
        "meetingsOutside": metrics["outside_work_events"],
        "busyHours": metrics["busy_hours"],
        "workHours": metrics["work_hours"],
        "timezoneMismatch": metrics["timezone_mismatch"],
        "hrCalendarMismatch": metrics["hr_mismatch"],
        "exceptions": build_recommendation_texts(employee, metrics),
        "statusNote": build_status_note(metrics),
        "metrics": metrics,
    }


def build_employee_list(
    employees: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    hr_profiles: List[Dict[str, Any]],
    absences: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    absences = absences or []
    hr_by_employee_id = {int(profile["employee_id"]): profile for profile in hr_profiles}
    result = []

    for employee in employees:
        metrics = calculate_employee_metrics(
            employee=employee,
            events=events,
            hr_profile=hr_by_employee_id.get(int(employee["id"])),
            absences=absences,
        )
        result.append({**employee, "metrics": metrics})

    return result


def build_employee_card(
    employee_id: int,
    employees: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    hr_profiles: List[Dict[str, Any]],
    absences: Optional[List[Dict[str, Any]]] = None,
) -> Optional[Dict[str, Any]]:
    absences = absences or []
    employee = next((item for item in employees if int(item["id"]) == employee_id), None)
    if not employee:
        return None

    hr_profile = next((item for item in hr_profiles if int(item["employee_id"]) == employee_id), None)
    metrics = calculate_employee_metrics(employee, events, hr_profile, absences)

    return {
        "employee": employee,
        "frontend_employee": to_frontend_employee(employee, metrics),
        "hr_profile": hr_profile,
        "events": employee_events(employee, events),
        "absences": employee_absences(employee, absences),
        "metrics": metrics,
        "recommendations": build_recommendation_texts(employee, metrics),
    }


def event_time_label(event: Dict[str, Any]) -> str:
    start = parse_datetime(event["start_datetime"])
    end = parse_datetime(event["end_datetime"])
    return f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"


def conflict_reason(event: Dict[str, Any], employee: Dict[str, Any]) -> str:
    start = parse_datetime(event["start_datetime"])
    end = parse_datetime(event["end_datetime"])

    if weekday_code(start) not in employee["work_days"]:
        return "Событие назначено в нерабочий день сотрудника."
    if start.time() < parse_time(employee["work_start"]):
        return "Событие начинается раньше заявленного рабочего времени."
    if end.time() > parse_time(employee["work_end"]):
        return "Событие заканчивается позже заявленного рабочего времени."
    return "Встреча выходит за пределы рабочего времени."


def conflict_severity(event: Dict[str, Any], employee: Dict[str, Any]) -> str:
    duration = event_duration_hours(event)
    start = parse_datetime(event["start_datetime"])
    end = parse_datetime(event["end_datetime"])
    work_start = parse_time(employee["work_start"])
    work_end = parse_time(employee["work_end"])

    if duration >= 1 or start.time() < work_start or end.time() > work_end:
        return "Высокая"
    return "Средняя"


def build_conflicts(
    employees: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    employees_by_id = {int(employee["id"]): employee for employee in employees}
    conflicts = []

    for event in events:
        employee = employees_by_id.get(int(event["employee_id"]))
        if not employee or not is_event_outside_work_time(event, employee):
            continue

        start = parse_datetime(event["start_datetime"])
        conflicts.append({
            "id": int(event["id"]),
            "employeeId": int(employee["id"]),
            "employee": employee["name"],
            "title": event["title"],
            "day": weekday_label(start),
            "time": event_time_label(event),
            "reason": conflict_reason(event, employee),
            "severity": conflict_severity(event, employee),
            "source": event.get("source", "calendar"),
            "type": event.get("type", "meeting"),
        })

    return conflicts


def build_data_mismatches(
    employees: List[Dict[str, Any]],
    hr_profiles: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    hr_by_employee_id = {int(profile["employee_id"]): profile for profile in hr_profiles}
    mismatches: List[Dict[str, Any]] = []

    for employee in employees:
        hr_profile = hr_by_employee_id.get(int(employee["id"]))
        if not hr_profile:
            continue

        if employee["timezone"] != hr_profile["hr_timezone"]:
            mismatches.append({
                "id": f"timezone-{employee['id']}",
                "employeeId": int(employee["id"]),
                "employee": employee["name"],
                "type": "timezone",
                "title": "Расхождение часового пояса",
                "reason": f"В профиле: {timezone_label(employee['timezone'])}, в HR: {timezone_label(hr_profile['hr_timezone'])}.",
                "severity": "Средняя",
            })

        if (
            employee["work_format"] != hr_profile["hr_work_format"]
            or employee["work_start"] != hr_profile["hr_work_start"]
            or employee["work_end"] != hr_profile["hr_work_end"]
        ):
            mismatches.append({
                "id": f"hr-{employee['id']}",
                "employeeId": int(employee["id"]),
                "employee": employee["name"],
                "type": "hr_profile",
                "title": "Расхождение с HR-профилем",
                "reason": "Рабочий формат или часы отличаются от HR-данных.",
                "severity": "Высокая",
            })

    return mismatches


def build_summary(
    employees: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    hr_profiles: List[Dict[str, Any]],
    absences: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    employee_items = build_employee_list(employees, events, hr_profiles, absences)
    total = len(employee_items)

    if not total:
        return {
            "total_employees": 0,
            "avg_risk": 0,
            "avg_schedule_actuality": 0,
            "avg_load": 0,
            "total_conflicts": 0,
            "calendar_conflicts": 0,
            "data_mismatches": 0,
            "total_outside_work_events": 0,
            "outdated_employees": 0,
            "high_risk_employees": 0,
            "risk_distribution": {},
            "teams": [],
        }

    metrics = [item["metrics"] for item in employee_items]
    conflicts = build_conflicts(employees, events)
    data_mismatches = build_data_mismatches(employees, hr_profiles)
    risk_distribution = {"низкий": 0, "средний": 0, "высокий": 0, "критический": 0}
    for metric in metrics:
        risk_distribution[metric["risk_status"]] += 1

    teams: Dict[str, Dict[str, Any]] = {}
    for item in employee_items:
        team = item["team"]
        teams.setdefault(team, {"team": team, "employees": 0, "avg_risk": 0, "total_conflicts": 0})
        teams[team]["employees"] += 1
        teams[team]["avg_risk"] += item["metrics"]["risk"]
        teams[team]["total_conflicts"] += item["metrics"]["calendar_conflict_count"]

    for team in teams.values():
        team["avg_risk"] = round2(team["avg_risk"] / team["employees"])

    return {
        "total_employees": total,
        "avg_risk": round2(sum(metric["risk"] for metric in metrics) / total),
        "avg_schedule_actuality": round2(sum(metric["schedule_actuality"] for metric in metrics) / total),
        "avg_load": round2(sum(metric["load"] for metric in metrics) / total),
        "total_conflicts": len(conflicts),
        "calendar_conflicts": len(conflicts),
        "data_mismatches": len(data_mismatches),
        "total_outside_work_events": sum(metric["outside_work_events"] for metric in metrics),
        "outdated_employees": sum(1 for metric in metrics if metric["days_since_update"] > MAX_DAYS_WITHOUT_UPDATE),
        "high_risk_employees": sum(1 for metric in metrics if metric["risk"] >= 0.50),
        "risk_distribution": risk_distribution,
        "teams": list(teams.values()),
    }


def build_frontend_summary(frontend_employees: List[Dict[str, Any]], conflicts: List[Dict[str, Any]]) -> Dict[str, int]:
    total = len(frontend_employees)
    if not total:
        return {"total": 0, "current": 0, "outdated": 0, "highRisk": 0, "conflicts": 0, "averageLoad": 0}

    return {
        "total": total,
        "current": sum(
            1
            for employee in frontend_employees
            if employee["metrics"]["schedule_actuality"] >= 0.70 and employee["metrics"]["risk"] < 0.50
        ),
        "outdated": sum(
            1 for employee in frontend_employees
            if employee["metrics"]["days_since_update"] > MAX_DAYS_WITHOUT_UPDATE
        ),
        "highRisk": sum(1 for employee in frontend_employees if employee["metrics"]["risk"] >= 0.50),
        "conflicts": len(conflicts),
        "averageLoad": round(sum(employee["metrics"]["load"] for employee in frontend_employees) / total * 100),
    }


def unavailability_reason(
    employee: Dict[str, Any],
    events: List[Dict[str, Any]],
    absences: List[Dict[str, Any]],
    day_label: str,
    hour: int,
    metrics: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    work_day_code = CODE_BY_RU[day_label]

    if work_day_code not in employee["work_days"]:
        return "нерабочий день"

    if hour < hour_int(employee["work_start"]) or hour >= hour_int(employee["work_end"]):
        return "вне рабочего времени"

    absence = is_absent_on_date(employee, absences, slot_date(day_label))
    if absence:
        return f"{absence['type']}"

    blocking_event = blocking_event_for_slot(employee, events, day_label, hour)
    if blocking_event:
        return f"занят: {blocking_event['title']}"

    if metrics and metrics.get("load", 0) >= 0.95:
        return "перегруз"

    return None


def build_availability(
    employees: List[Dict[str, Any]],
    events: Optional[List[Dict[str, Any]]] = None,
    hr_profiles: Optional[List[Dict[str, Any]]] = None,
    absences: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    events = events or []
    hr_profiles = hr_profiles or []
    absences = absences or []
    days = ["Пн", "Вт", "Ср", "Чт", "Пт"]
    hours = range(8, 21)
    hr_by_employee_id = {int(profile["employee_id"]): profile for profile in hr_profiles}
    metrics_by_employee_id = {
        int(employee["id"]): calculate_employee_metrics(employee, events, hr_by_employee_id.get(int(employee["id"])), absences)
        for employee in employees
    }
    rows = []

    for day in days:
        slots = []
        for hour in hours:
            available = []
            missing = []
            missing_details = []

            for employee in employees:
                metrics = metrics_by_employee_id[int(employee["id"])]
                reason = unavailability_reason(employee, events, absences, day, hour, metrics)
                if reason:
                    missing.append(employee["name"])
                    missing_details.append({"employee": employee["name"], "reason": reason})
                else:
                    available.append(employee)

            if len(available) == len(employees) and employees:
                slot_type = "all"
            elif len(available) >= max(1, round(len(employees) * 0.65)):
                slot_type = "majority"
            else:
                slot_type = "weak"

            slots.append({
                "hour": hour,
                "count": len(available),
                "type": slot_type,
                "missing": missing,
                "missingDetails": missing_details,
            })
        rows.append({"day": day, "slots": slots})

    return rows


def build_best_slots(
    employees: List[Dict[str, Any]],
    events: Optional[List[Dict[str, Any]]] = None,
    hr_profiles: Optional[List[Dict[str, Any]]] = None,
    absences: Optional[List[Dict[str, Any]]] = None,
    limit: int = 3,
) -> List[Dict[str, Any]]:
    all_slots = []
    for row in build_availability(employees, events, hr_profiles, absences):
        for slot in row["slots"]:
            all_slots.append({
                "label": f"{row['day']}, {slot['hour']}:00-{slot['hour'] + 1}:00",
                "day": row["day"],
                "hour": slot["hour"],
                "count": slot["count"],
                "missing": slot["missing"],
                "missingDetails": slot.get("missingDetails", []),
            })

    return [
        {
            "label": slot["label"],
            "count": slot["count"],
            "missing": slot["missing"],
            "missingDetails": slot["missingDetails"],
        }
        for slot in sorted(all_slots, key=lambda item: (-item["count"], len(item["missing"]), item["hour"], item["day"]))[:limit]
    ]


def build_recommendations(
    employees: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    hr_profiles: List[Dict[str, Any]],
    absences: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, str]]:
    absences = absences or []
    hr_by_employee_id = {int(profile["employee_id"]): profile for profile in hr_profiles}
    recommendations: List[Dict[str, str]] = []

    for employee in employees:
        metrics = calculate_employee_metrics(
            employee,
            events,
            hr_by_employee_id.get(int(employee["id"])),
            absences,
        )

        if metrics["risk"] >= 0.50 or metrics["days_since_update"] > 60:
            recommendations.append({
                "type": "График",
                "title": f"Попросить {employee['name']} подтвердить рабочий график",
                "reason": f"Риск {percent(metrics['risk'])}%, обновление было {metrics['days_since_update']} дней назад.",
                "priority": "Срочно" if metrics["risk"] >= 0.75 else "Важно",
            })

        if metrics["timezone_mismatch"]:
            recommendations.append({
                "type": "Часовой пояс",
                "title": f"Проверить часовой пояс: {employee['name']}",
                "reason": "Часовой пояс сотрудника отличается от HR-профиля или фактической активности.",
                "priority": "Важно",
            })

        if metrics["load"] >= 0.80:
            recommendations.append({
                "type": "Нагрузка",
                "title": f"Не назначать новые встречи: {employee['name']}",
                "reason": f"Загрузка {percent(metrics['load'])}%, сотрудник близок к перегрузу.",
                "priority": "Срочно",
            })

        if metrics["hr_mismatch"]:
            recommendations.append({
                "type": "HR-данные",
                "title": f"Сверить HR-профиль: {employee['name']}",
                "reason": "Рабочий формат или часы в HR-системе отличаются от календарного профиля.",
                "priority": "Важно",
            })

        for absence in employee_absences(employee, absences):
            recommendations.append({
                "type": "Исключение",
                "title": f"Учесть отсутствие: {employee['name']}",
                "reason": f"{absence['type']}: {absence['start_date']} — {absence['end_date']}.",
                "priority": "Важно",
            })

    for conflict in build_conflicts(employees, events)[:3]:
        recommendations.append({
            "type": "Встреча",
            "title": f"Перенести: {conflict['title']}",
            "reason": f"{conflict['employee']}, {conflict['day']} {conflict['time']}. {conflict['reason']}",
            "priority": "Срочно" if conflict["severity"] == "Высокая" else "Важно",
        })

    for slot in build_best_slots(employees, events, hr_profiles, absences, limit=1):
        recommendations.append({
            "type": "Встреча",
            "title": "Использовать лучшее командное окно",
            "reason": f"Рекомендуемый слот: {slot['label']}. Доступно {slot['count']} сотрудников.",
            "priority": "Планово",
        })

    return sorted(recommendations, key=lambda item: PRIORITY_ORDER.get(item["priority"], 9))


def build_roadmap(summary: Dict[str, int]) -> List[Dict[str, str]]:
    return [
        {
            "step": "1",
            "title": "Подтвердить графики с высоким риском",
            "owner": "HR",
            "deadline": "Сегодня",
            "state": "Срочно" if summary["highRisk"] else "Планово",
        },
        {
            "step": "2",
            "title": "Проверить часовые пояса и HR-расхождения",
            "owner": "Руководитель",
            "deadline": "До конца дня",
            "state": "Важно",
        },
        {
            "step": "3",
            "title": "Перенести регулярные встречи вне рабочего времени",
            "owner": "PM",
            "deadline": "Завтра",
            "state": "В работе" if summary["conflicts"] else "Готово",
        },
    ]


def build_worktime_overview(
    employees: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    hr_profiles: List[Dict[str, Any]],
    absences: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    employee_items = build_employee_list(employees, events, hr_profiles, absences)
    frontend_employees = [to_frontend_employee(item, item["metrics"]) for item in employee_items]
    conflicts = build_conflicts(employees, events)
    summary = build_frontend_summary(frontend_employees, conflicts)

    return {
        "employees": frontend_employees,
        "events": conflicts,
        "roadmap": build_roadmap(summary),
        "summary": summary,
        "recommendations": build_recommendations(employees, events, hr_profiles, absences),
        "bestSlots": build_best_slots(employees, events, hr_profiles, absences),
        "availability": build_availability(employees, events, hr_profiles, absences),
        "dataMismatches": build_data_mismatches(employees, hr_profiles),
    }
