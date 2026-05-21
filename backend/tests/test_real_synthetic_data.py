from fastapi.testclient import TestClient

from app.data_loader import load_absences, load_employees, load_events, load_hr_profiles
from app.main import app

client = TestClient(app)


def test_real_synthetic_data_loads():
    employees = load_employees()
    events = load_events()
    hr_profiles = load_hr_profiles()
    absences = load_absences()

    assert len(employees) >= 10
    assert len(events) >= 30
    assert len(hr_profiles) >= 10
    assert len(absences) >= 2


def test_real_synthetic_data_has_no_orphan_events_or_absences():
    employees = load_employees()
    events = load_events()
    absences = load_absences()

    employee_ids = {employee["id"] for employee in employees}

    assert [event for event in events if event["employee_id"] not in employee_ids] == []
    assert [absence for absence in absences if absence["employee_id"] not in employee_ids] == []


def test_real_synthetic_key_endpoints_return_200():
    endpoints = [
        "/health/data",
        "/data/source",
        "/schemas",
        "/api/worktime/overview",
        "/api/worktime/overview?department=Product",
        "/analytics/summary",
        "/analytics/groups",
        "/analytics/data-quality",
        "/notifications",
        "/meeting-slots",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, endpoint
