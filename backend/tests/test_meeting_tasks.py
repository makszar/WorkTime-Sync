from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tasks_are_enriched():
    r = client.get("/tasks?user_id=u1")
    assert r.status_code == 200
    tasks = r.json()
    assert tasks
    assert "employee_name" in tasks[0]
    assert "creator_name" in tasks[0]

def test_create_meeting_task_success():
    r = client.post("/tasks?user_id=u1", json={
        "employee_id": 5,
        "type": "meeting_outside_work_approval",
        "title": "Согласовать встречу после графика",
        "description": "Нужно подтвердить участие во встрече вне рабочего времени.",
        "due_date": "2026-05-24",
        "related_event_id": 2,
        "meeting_action": "approve_outside_work"
    })
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "meeting_outside_work_approval"
    assert data["related_event"]["id"] == 2

def test_manager_cannot_assign_outside_department():
    r = client.post("/tasks?user_id=u1", json={
        "employee_id": 12,
        "type": "confirm_schedule",
        "title": "Чужой отдел",
        "description": "Попытка создать задачу вне отдела.",
        "due_date": "2026-05-24"
    })
    assert r.status_code == 403

def test_related_event_not_found():
    r = client.post("/tasks?user_id=u1", json={
        "employee_id": 5,
        "type": "meeting_confirmation",
        "title": "Несуществующая встреча",
        "description": "Проверка валидации.",
        "due_date": "2026-05-24",
        "related_event_id": 9999
    })
    assert r.status_code == 400

def test_task_event_mismatch():
    r = client.post("/tasks?user_id=u1", json={
        "employee_id": 5,
        "type": "meeting_confirmation",
        "title": "Встреча другого сотрудника",
        "description": "Проверка mismatch.",
        "due_date": "2026-05-24",
        "related_event_id": 12
    })
    assert r.status_code == 400

def test_reject_requires_comment():
    r = client.patch("/tasks/10/status?user_id=emp5", json={"status": "rejected", "employee_comment": ""})
    assert r.status_code == 400

def test_employee_me_contains_meeting_task_groups():
    r = client.get("/employees/me?user_id=emp5")
    assert r.status_code == 200
    data = r.json()
    assert "pendingTasks" in data
    assert "completedTasks" in data
    assert "tasksByType" in data
    assert "meetingTasks" in data
    assert "conflictingEvents" in data

def test_company_analytics_task_metrics():
    r = client.get("/analytics/company?user_id=u0")
    assert r.status_code == 200
    data = r.json()
    assert "tasksByDepartment" in data
    assert "taskStatusCounts" in data
    assert "scheduleConfirmationRate" in data

def test_hr_dashboard_task_statuses():
    r = client.get("/analytics/hr-dashboard?user_id=u_hr")
    assert r.status_code == 200
    data = r.json()
    assert "pendingTasks" in data
    assert "rejectedTasks" in data
    assert "changeRequestedConfirmations" in data

def test_data_quality_checks_task_relations():
    r = client.get("/analytics/data-quality")
    assert r.status_code == 200
    data = r.json()
    assert data["orphan_related_event_id"] == []
    assert data["task_event_mismatch"] == []
    assert data["invalid_task_types"] == []
    assert data["invalid_task_statuses"] == []
