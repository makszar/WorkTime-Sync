from app.analytics import (
    DEMO_TODAY,
    build_availability,
    build_best_slots,
    build_conflicts,
    build_groups,
    build_notifications,
    build_risk_explanation,
    calculate_employee_metrics,
)


def sample_employee(**overrides):
    employee = {
        "id": 1,
        "name": "Test User",
        "team": "Backend",
        "role": "Developer",
        "timezone": "Europe/Moscow",
        "work_start": "09:00",
        "work_end": "18:00",
        "work_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "work_format": "remote",
        "last_update_date": "2026-05-01",
    }
    employee.update(overrides)
    return employee


def test_metrics_split_calendar_conflicts_and_data_mismatches():
    employee = sample_employee()
    events = [
        {
            "id": 1,
            "employee_id": 1,
            "title": "Late meeting",
            "start_datetime": "2026-05-19T19:30:00",
            "end_datetime": "2026-05-19T20:00:00",
            "source": "calendar",
            "type": "meeting",
        }
    ]
    hr_profile = {
        "employee_id": 1,
        "hr_timezone": "Europe/Moscow",
        "hr_work_format": "office",
        "hr_work_start": "09:00",
        "hr_work_end": "18:00",
    }

    metrics = calculate_employee_metrics(employee, events, hr_profile, [], today=DEMO_TODAY)

    assert metrics["calendar_conflict_count"] == 1
    assert metrics["data_mismatch_count"] == 1
    assert metrics["issue_count"] == 2
    assert metrics["conflict_count"] == 1
    assert metrics["risk"] > 0


def test_build_conflicts_returns_event_level_conflicts():
    employee = sample_employee()
    events = [
        {
            "id": 1,
            "employee_id": 1,
            "title": "Early meeting",
            "start_datetime": "2026-05-18T08:00:00",
            "end_datetime": "2026-05-18T08:30:00",
            "source": "calendar",
            "type": "meeting",
        }
    ]

    conflicts = build_conflicts([employee], events)
    assert len(conflicts) == 1
    assert conflicts[0]["reason"] == "Событие начинается раньше заявленного рабочего времени."


def test_availability_blocks_calendar_events_and_absences():
    employees = [sample_employee()]
    events = [
        {
            "id": 1,
            "employee_id": 1,
            "title": "Busy block",
            "start_datetime": "2026-05-18T10:00:00",
            "end_datetime": "2026-05-18T11:00:00",
            "source": "calendar",
            "type": "meeting",
        }
    ]
    absences = [
        {"id": 1, "employee_id": 1, "type": "отпуск", "start_date": "2026-05-20", "end_date": "2026-05-20"}
    ]

    rows = build_availability(employees, events, [], absences)
    monday = next(row for row in rows if row["day"] == "Пн")
    wednesday = next(row for row in rows if row["day"] == "Ср")

    busy_slot = next(slot for slot in monday["slots"] if slot["hour"] == 10)
    absence_slot = next(slot for slot in wednesday["slots"] if slot["hour"] == 10)

    assert busy_slot["count"] == 0
    assert "Busy block" in busy_slot["missingDetails"][0]["reason"]
    assert absence_slot["count"] == 0
    assert absence_slot["missingDetails"][0]["reason"] == "отпуск"


def test_best_slots_are_limited_and_sorted():
    employees = [sample_employee()]
    slots = build_best_slots(employees, [], [], [], limit=3)
    assert len(slots) == 3
    assert slots[0]["count"] == 1


def test_groups_detect_high_load_and_confirmation_need():
    employee = sample_employee(last_update_date="2025-12-01")
    events = [
        {
            "id": 1,
            "employee_id": 1,
            "title": "Long focus",
            "start_datetime": "2026-05-18T09:00:00",
            "end_datetime": "2026-05-22T18:00:00",
            "source": "task_tracker",
            "type": "focus",
        }
    ]
    groups = build_groups([employee], events, [], [])
    assert groups["outdated"]
    assert groups["highLoad"]
    assert groups["needsConfirmation"]


def test_risk_explanation_contains_weighted_factors():
    employee = sample_employee(last_update_date="2025-12-01")
    explanation = build_risk_explanation(1, [employee], [], [], [])
    assert explanation is not None
    assert explanation["employeeId"] == 1
    assert explanation["formula"]
    assert any(factor["factor"] == "days_since_update" for factor in explanation["factors"])


def test_notifications_are_generated_from_risks():
    employee = sample_employee(last_update_date="2025-12-01")
    notifications = build_notifications([employee], [], [], [])
    assert notifications
    assert notifications[0]["recipientRole"] in {"HR", "Руководитель", "PM"}
