from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_worktime_overview_contract():
    response = client.get("/api/worktime/overview")
    assert response.status_code == 200
    data = response.json()

    assert set(["employees", "events", "roadmap", "summary", "recommendations", "bestSlots"]).issubset(data)
    assert len(data["employees"]) >= 5
    assert data["summary"]["total"] == len(data["employees"])
    assert len(data["bestSlots"]) <= 3


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
    assert {"label", "count", "missing"}.issubset(slots[0])


def test_data_mismatches_endpoint():
    response = client.get("/analytics/data-mismatches")
    assert response.status_code == 200
    mismatches = response.json()
    assert isinstance(mismatches, list)
