from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional

WEEKDAY_MAP = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun",
}


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def parse_time(value: str) -> time:
    return time.fromisoformat(value)


def round2(value: float) -> float:
    return round(value, 2)


def event_duration_hours(event: Dict[str, Any]) -> float:
    start = parse_datetime(event["start_datetime"])
    end = parse_datetime(event["end_datetime"])
    return max(0, (end - start).total_seconds() / 3600)


def is_event_outside_work_time(event: Dict[str, Any], employee: Dict[str, Any]) -> bool:
    """Событие считается конфликтным, если оно не попадает в рабочие дни или часы."""
    start = parse_datetime(event["start_datetime"])
    end = parse_datetime(event["end_datetime"])

    weekday = WEEKDAY_MAP[start.weekday()]
    if weekday not in employee["work_days"]:
        return True

    work_start = parse_time(employee["work_start"])
    work_end = parse_time(employee["work_end"])

    return start.time() < work_start or end.time() > work_end


def count_work_days(start_date: date, end_date: date, work_days: List[str]) -> int:
    days = 0
    current = start_date
    while current <= end_date:
        if WEEKDAY_MAP[current.weekday()] in work_days:
            days += 1
        current += timedelta(days=1)
    return days


def daily_work_hours(employee: Dict[str, Any]) -> float:
    start = datetime.combine(date.today(), parse_time(employee["work_start"]))
    end = datetime.combine(date.today(), parse_time(employee["work_end"]))
    return max(0, (end - start).total_seconds() / 3600)


def risk_status(risk: float) -> str:
    if risk < 0.25:
        return "низкий"
    if risk < 0.50:
        return "средний"
    if risk < 0.75:
        return "высокий"
    return "критический"


def calculate_employee_metrics(
    employee: Dict[str, Any],
    events: List[Dict[str, Any]],
    hr_profile: Optional[Dict[str, Any]],
    today: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Считает метрики сотрудника.
    Формулы оставлены простыми, чтобы их можно было быстро объяснить на защите.
    """
    today = today or date.today()
    employee_events = [event for event in events if int(event["employee_id"]) == int(employee["id"])]

    days_since_update = (today - parse_date(employee["last_update_date"])).days
    days_since_update = max(0, days_since_update)

    # A = max(0, 1 - days_since_update / 90)
    schedule_actuality = max(0, 1 - days_since_update / 90)

    outside_work_events = sum(
        1 for event in employee_events if is_event_outside_work_time(event, employee)
    )
    total_events = len(employee_events)

    # C = events_outside_work_time / total_events
    outside_work_ratio = outside_work_events / total_events if total_events else 0

    busy_hours = sum(event_duration_hours(event) for event in employee_events)

    if employee_events:
        event_dates = [parse_datetime(event["start_datetime"]).date() for event in employee_events]
        period_start = min(event_dates)
        period_end = max(event_dates)
        work_days_count = count_work_days(period_start, period_end, employee["work_days"])
    else:
        work_days_count = 5

    work_hours = daily_work_hours(employee) * work_days_count

    # L = busy_hours / work_hours
    load = busy_hours / work_hours if work_hours else 0

    timezone_mismatch = 0
    hr_mismatch = 0
    if hr_profile:
        timezone_mismatch = int(employee["timezone"] != hr_profile["hr_timezone"])
        hr_mismatch = int(
            employee["work_format"] != hr_profile["hr_work_format"]
            or employee["work_start"] != hr_profile["hr_work_start"]
            or employee["work_end"] != hr_profile["hr_work_end"]
        )

    # Упрощённый счётчик конфликтов для MVP.
    conflict_count = outside_work_events + timezone_mismatch + hr_mismatch

    # R = 0.30 * (1 - A) + 0.25 * C + 0.25 * L + 0.10 * timezone_mismatch + 0.10 * hr_mismatch
    risk = (
        0.30 * (1 - schedule_actuality)
        + 0.25 * outside_work_ratio
        + 0.25 * load
        + 0.10 * timezone_mismatch
        + 0.10 * hr_mismatch
    )
    risk = min(1, max(0, risk))

    return {
        "days_since_update": days_since_update,
        "schedule_actuality": round2(schedule_actuality),
        "outside_work_events": outside_work_events,
        "total_events": total_events,
        "outside_work_ratio": round2(outside_work_ratio),
        "busy_hours": round2(busy_hours),
        "work_hours": round2(work_hours),
        "load": round2(load),
        "timezone_mismatch": timezone_mismatch,
        "hr_mismatch": hr_mismatch,
        "conflict_count": conflict_count,
        "risk": round2(risk),
        "risk_status": risk_status(risk),
    }


def build_recommendations(employee: Dict[str, Any], metrics: Dict[str, Any]) -> List[str]:
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

    if not recommendations:
        recommendations.append("Критичных проблем не найдено, график выглядит актуальным.")

    return recommendations


def build_employee_list(
    employees: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    hr_profiles: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    hr_by_employee_id = {int(profile["employee_id"]): profile for profile in hr_profiles}
    result = []

    for employee in employees:
        metrics = calculate_employee_metrics(
            employee=employee,
            events=events,
            hr_profile=hr_by_employee_id.get(int(employee["id"])),
        )
        result.append({**employee, "metrics": metrics})

    return result


def build_employee_card(
    employee_id: int,
    employees: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    hr_profiles: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    employee = next((item for item in employees if int(item["id"]) == employee_id), None)
    if not employee:
        return None

    employee_events = [event for event in events if int(event["employee_id"]) == employee_id]
    hr_profile = next((item for item in hr_profiles if int(item["employee_id"]) == employee_id), None)
    metrics = calculate_employee_metrics(employee, events, hr_profile)

    return {
        "employee": employee,
        "hr_profile": hr_profile,
        "events": employee_events,
        "metrics": metrics,
        "recommendations": build_recommendations(employee, metrics),
    }


def build_summary(
    employees: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    hr_profiles: List[Dict[str, Any]],
) -> Dict[str, Any]:
    employee_items = build_employee_list(employees, events, hr_profiles)
    total = len(employee_items)

    if total == 0:
        return {
            "total_employees": 0,
            "avg_risk": 0,
            "avg_schedule_actuality": 0,
            "avg_load": 0,
            "total_conflicts": 0,
            "risk_distribution": {},
            "teams": [],
        }

    metrics = [item["metrics"] for item in employee_items]
    risk_distribution = {"низкий": 0, "средний": 0, "высокий": 0, "критический": 0}
    for metric in metrics:
        risk_distribution[metric["risk_status"]] += 1

    teams = {}
    for item in employee_items:
        team = item["team"]
        teams.setdefault(team, {"team": team, "employees": 0, "avg_risk": 0, "total_conflicts": 0})
        teams[team]["employees"] += 1
        teams[team]["avg_risk"] += item["metrics"]["risk"]
        teams[team]["total_conflicts"] += item["metrics"]["conflict_count"]

    for team in teams.values():
        team["avg_risk"] = round2(team["avg_risk"] / team["employees"])

    return {
        "total_employees": total,
        "avg_risk": round2(sum(metric["risk"] for metric in metrics) / total),
        "avg_schedule_actuality": round2(sum(metric["schedule_actuality"] for metric in metrics) / total),
        "avg_load": round2(sum(metric["load"] for metric in metrics) / total),
        "total_conflicts": sum(metric["conflict_count"] for metric in metrics),
        "total_outside_work_events": sum(metric["outside_work_events"] for metric in metrics),
        "risk_distribution": risk_distribution,
        "teams": list(teams.values()),
    }
