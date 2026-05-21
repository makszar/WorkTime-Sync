from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


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
    assert data["employees"] >= 10
    assert data["events"] >= 30
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
    response = client.post("/auth/login", json={"login": "product_manager", "password": "test1"})
    assert response.status_code == 200
    data = response.json()

    assert data["token"] == "demo-product_manager"
    assert data["user"]["department"] == "Product"
    assert "password" not in data["user"]


def test_login_wrong_password():
    response = client.post("/auth/login", json={"login": "product_manager", "password": "wrong"})
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
    response = client.get("/api/worktime/overview?department=Product")
    assert response.status_code == 200
    data = response.json()

    assert data["employees"]
    assert data["total_synthetic_employees"] >= len(data["employees"])
    assert data["meta"]["department"] == "Product"
    assert all(employee["team"] == "Product" for employee in data["employees"])


def test_employees_department_filter():
    response = client.get("/employees?department=QA")
    assert response.status_code == 200
    employees = response.json()

    assert employees
    assert all(employee["team"] == "QA" for employee in employees)


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

    assert quality["employees"] >= 10
    assert quality["events"] >= 30
    assert quality["orphan_events"] == []
    assert quality["orphan_absences"] == []
    assert quality["invalid_event_ranges"] == []
    assert quality["invalid_absence_ranges"] == []
    assert "Product" in quality["teams"]


def test_groups_endpoint():
    response = client.get("/analytics/groups")
    assert response.status_code == 200
    groups = response.json()
    assert {"actual", "outdated", "outsideWorkMeetings", "highLoad", "timezoneConflict", "hrMismatch", "needsConfirmation"}.issubset(groups)
    assert groups["highLoad"]


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
    response = client.get("/notifications?department=HR")
    assert response.status_code == 200
    notifications = response.json()
    assert isinstance(notifications, list)
