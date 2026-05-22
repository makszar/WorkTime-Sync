from fastapi.testclient import TestClient

from app.data_loader import load_employees
from app.main import app

client = TestClient(app)


def _first_department() -> str:
    employees = load_employees()
    departments = sorted({employee["team"] for employee in employees})
    assert departments
    return departments[0]


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_data():
    response = client.get("/health/data")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["data_source"].endswith("data/synthetic")
    assert data["employees"] >= 5
    assert data["events"] >= 1
    assert data["datasets"]["employees"].endswith("employees.csv")


def test_data_source_endpoint():
    response = client.get("/data/source")
    assert response.status_code == 200
    data = response.json()

    assert data["active_source"].endswith("data/synthetic")
    assert "employees" in data["datasets"]
    assert "events" in data["datasets"]


def test_schemas_endpoint():
    response = client.get("/schemas")
    assert response.status_code == 200
    schemas = response.json()

    assert "employees" in schemas
    assert "events" in schemas
    assert "work_days" in schemas["employees"]


def test_login_success():
    response = client.post("/auth/login", json={"login": "zarix", "password": "i9VUibm6"})
    assert response.status_code == 200
    data = response.json()

    assert data["token"] == "demo-zarix"
    assert data["user"]["department"] == "Core Platform"
    assert "password" not in data["user"]


def test_login_wrong_password():
    response = client.post("/auth/login", json={"login": "zarix", "password": "wrong"})
    assert response.status_code == 401


def test_worktime_overview_contract():
    response = client.get("/api/worktime/overview")
    assert response.status_code == 200
    data = response.json()

    assert set(["employees", "events", "roadmap", "summary", "recommendations", "bestSlots", "notifications", "groups", "meta"]).issubset(data)
    assert len(data["employees"]) >= 5
    assert data["summary"]["total"] == len(data["employees"])
    assert len(data["bestSlots"]) <= 3
    assert data["meta"]["data_source"].endswith("data/synthetic")


def test_worktime_overview_department_filter():
    department = _first_department()
    response = client.get(f"/api/worktime/overview?department={department}")
    assert response.status_code == 200
    data = response.json()

    assert data["employees"]
    assert data["total_synthetic_employees"] >= len(data["employees"])
    assert data["meta"]["department"] == department
    assert all(employee["team"] == department for employee in data["employees"])


def test_employees_department_filter():
    department = _first_department()
    response = client.get(f"/employees?department={department}")
    assert response.status_code == 200
    employees = response.json()

    assert employees
    assert all(employee["team"] == department for employee in employees)


def test_conflicts_endpoint():
    response = client.get("/analytics/conflicts")
    assert response.status_code == 200
    conflicts = response.json()
    assert isinstance(conflicts, list)
    assert conflicts
    assert {"employee", "title", "day", "time", "reason", "severity"}.issubset(conflicts[0])


def test_availability_endpoint_uses_missing_reasons():
    response = client.get("/analytics/availability")
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 5

    first_slot = rows[0]["slots"][0]
    assert {"hour", "count", "type", "missing", "missingDetails"}.issubset(first_slot)


def test_meeting_slots_endpoint():
    response = client.get("/meeting-slots")
    assert response.status_code == 200
    slots = response.json()
    assert 1 <= len(slots) <= 3
    assert {"label", "count", "missing", "missingDetails"}.issubset(slots[0])


def test_data_mismatches_endpoint():
    response = client.get("/analytics/data-mismatches")
    assert response.status_code == 200
    mismatches = response.json()
    assert isinstance(mismatches, list)


def test_data_quality_endpoint():
    response = client.get("/analytics/data-quality")
    assert response.status_code == 200
    quality = response.json()

    assert quality["employees"] >= 5
    assert quality["events"] >= 1
    assert quality["orphan_events"] == []
    assert quality["orphan_absences"] == []
    assert quality["invalid_event_ranges"] == []
    assert quality["invalid_absence_ranges"] == []

    actual_departments = {employee["team"] for employee in load_employees()}
    assert set(quality["teams"]) == actual_departments


def test_groups_endpoint():
    response = client.get("/analytics/groups")
    assert response.status_code == 200
    groups = response.json()
    assert {"actual", "outdated", "outsideWorkMeetings", "highLoad", "timezoneConflict", "hrMismatch", "needsConfirmation"}.issubset(groups)
    assert isinstance(groups["highLoad"], list)


def test_risk_explanation_endpoint():
    response = client.get("/employees/4/risk-explanation")
    assert response.status_code == 200
    explanation = response.json()
    assert explanation["employeeId"] == 4
    assert "formula" in explanation
    assert len(explanation["factors"]) >= 5
    assert explanation["recommendedActions"]


def test_risk_explanation_unknown_employee():
    response = client.get("/employees/999/risk-explanation")
    assert response.status_code == 404


def test_notifications_endpoint():
    response = client.get("/notifications")
    assert response.status_code == 200
    notifications = response.json()
    assert isinstance(notifications, list)
    assert notifications
    assert {"recipientRole", "title", "reason", "priority", "action"}.issubset(notifications[0])


def test_notifications_department_filter():
    department = _first_department()
    response = client.get(f"/notifications?department={department}")
    assert response.status_code == 200
    notifications = response.json()
    assert isinstance(notifications, list)


def test_demo_dataset_has_25_employees_and_5_departments():
    employees = load_employees()
    departments = sorted({employee["team"] for employee in employees})

    assert len(employees) == 25
    assert departments == ["Core Platform", "Delivery", "People Ops", "Product UI", "Quality"]
    assert all(sum(1 for employee in employees if employee["team"] == department) == 5 for department in departments)


def test_required_demo_logins():
    profiles = [
        ("zarix", "i9VUibm6", "Core Platform"),
        ("lixxxa", "test1", "Product UI"),
        ("baftype", "test2", "People Ops"),
        ("ssdshkaaa", "test3", "Delivery"),
        ("agentemy", "test4", "Quality"),
    ]

    for login, password, department in profiles:
        response = client.post("/auth/login", json={"login": login, "password": password})
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["login"] == login
        assert data["user"]["department"] == department
        assert "password" not in data["user"]
