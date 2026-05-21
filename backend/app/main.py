from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.analytics import (
    build_availability,
    build_best_slots,
    build_conflicts,
    build_data_mismatches,
    build_employee_card,
    build_employee_list,
    build_groups,
    build_notifications,
    build_recommendations,
    build_risk_explanation,
    build_summary,
    build_worktime_overview,
)
from app.data_loader import (
    get_data_source_info,
    get_schema_definitions,
    load_absences,
    load_employees,
    load_events,
    load_hr_profiles,
    save_uploaded_table,
)
from app.data_quality import build_data_quality
from app.models import AvailabilityDay, Conflict, DataMismatch, MeetingSlot, Notification, Recommendation, RiskExplanation

PROJECT_ROOT = Path(__file__).resolve().parents[2]
USERS_PATH = PROJECT_ROOT / "data" / "synthetic" / "users.json"

DEFAULT_USERS = [
    {
        "id": "u1",
        "login": "core_manager",
        "password": "test1",
        "name": "Core Platform Manager",
        "role": "Руководитель отдела",
        "department": "Core Platform",
    },
    {
        "id": "u2",
        "login": "product_ui_manager",
        "password": "test2",
        "name": "Product UI Manager",
        "role": "Руководитель отдела",
        "department": "Product UI",
    },
    {
        "id": "u3",
        "login": "people_ops_manager",
        "password": "test3",
        "name": "People Ops Manager",
        "role": "HR",
        "department": "People Ops",
    },
    {
        "id": "u4",
        "login": "delivery_manager",
        "password": "test4",
        "name": "Delivery Manager",
        "role": "Руководитель отдела",
        "department": "Delivery",
    },
    {
        "id": "u5",
        "login": "quality_manager",
        "password": "test5",
        "name": "Quality Manager",
        "role": "Руководитель отдела",
        "department": "Quality",
    },
]


class LoginRequest(BaseModel):
    login: str
    password: str


app = FastAPI(
    title="WorkTime Sync Backend",
    description="FastAPI backend для фронтенда WorkTime Sync и аналитики рабочего времени.",
    version="1.4.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def public_user(user: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in user.items() if key != "password"}


def load_users() -> list[dict[str, Any]]:
    if not USERS_PATH.exists():
        return DEFAULT_USERS

    with USERS_PATH.open("r", encoding="utf-8") as file:
        users = json.load(file)

    if not isinstance(users, list):
        raise HTTPException(status_code=500, detail="users.json должен содержать список профилей")

    return users


def filter_by_department(
    department: str | None,
    employees: list[dict[str, Any]],
    events: list[dict[str, Any]],
    hr_profiles: list[dict[str, Any]],
    absences: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    if not department:
        return employees, events, hr_profiles, absences

    scoped_employees = [employee for employee in employees if employee.get("team") == department]
    employee_ids = {int(employee["id"]) for employee in scoped_employees}

    return (
        scoped_employees,
        [event for event in events if int(event["employee_id"]) in employee_ids],
        [profile for profile in hr_profiles if int(profile["employee_id"]) in employee_ids],
        [absence for absence in absences if int(absence["employee_id"]) in employee_ids],
    )


def departments_from_employees(employees: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"name": team, "count": sum(1 for employee in employees if employee.get("team") == team)}
        for team in sorted({employee.get("team") for employee in employees if employee.get("team")})
    ]


def get_data():
    """For MVP we reread JSON/CSV files on every request.

    This makes demos and uploads simple: after replacing a file, the next API
    call immediately uses the new data.
    """
    try:
        employees = load_employees()
        events = load_events()
        hr_profiles = load_hr_profiles()
        absences = load_absences()
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    return employees, events, hr_profiles, absences


@app.post("/auth/login")
def login(payload: LoginRequest):
    requested_login = payload.login.strip()
    users = load_users()
    user = next(
        (
            item
            for item in users
            if item.get("login") == requested_login and item.get("password") == payload.password
        ),
        None,
    )

    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    return {
        "token": f"demo-{user['login']}",
        "user": public_user(user),
    }


@app.get("/")
def root():
    return {
        "service": "WorkTime Sync Backend",
        "docs": "/docs",
        "frontend_endpoint": "/api/worktime/overview",
        "auth_endpoint": "/auth/login",
        "endpoints": [
            "/auth/login",
            "/health",
            "/health/data",
            "/data/source",
            "/schemas",
            "/api/worktime/overview",
            "/employees",
            "/employees/{employee_id}",
            "/employees/{employee_id}/risk-explanation",
            "/analytics/summary",
            "/analytics/conflicts",
            "/analytics/data-mismatches",
            "/analytics/data-quality",
            "/analytics/availability",
            "/analytics/groups",
            "/recommendations",
            "/notifications",
            "/meeting-slots",
            "/upload/{dataset}",
        ],
    }


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.get("/health/data")
def health_data():
    employees, events, hr_profiles, absences = get_data()
    source_info = get_data_source_info()
    return {
        "status": "ok",
        "data_source": source_info["active_source"],
        "employees": len(employees),
        "events": len(events),
        "hr_profiles": len(hr_profiles),
        "absences": len(absences),
        "datasets": source_info["datasets"],
    }


@app.get("/data/source")
def get_data_source():
    return get_data_source_info()


@app.get("/schemas")
def get_schemas():
    return get_schema_definitions()


@app.get("/api/worktime/overview")
def get_worktime_overview(department: str | None = None):
    employees, events, hr_profiles, absences = get_data()
    scoped = filter_by_department(department, employees, events, hr_profiles, absences)
    result = build_worktime_overview(*scoped)
    source_info = get_data_source_info()

    result["total_synthetic_employees"] = len(employees)
    result["departments"] = departments_from_employees(employees)
    result["meta"] = {
        "backend_version": app.version,
        "data_source": source_info["active_source"],
        "department": department,
        "employees_count": len(scoped[0]),
        "events_count": len(scoped[1]),
        "hr_profiles_count": len(scoped[2]),
        "absences_count": len(scoped[3]),
        "total_employees_count": len(employees),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }
    return result


@app.get("/employees")
def get_employees(department: str | None = None):
    employees, events, hr_profiles, absences = get_data()
    scoped = filter_by_department(department, employees, events, hr_profiles, absences)
    return build_employee_list(*scoped)


@app.get("/employees/frontend")
def get_frontend_employees(department: str | None = None):
    employees, events, hr_profiles, absences = get_data()
    scoped = filter_by_department(department, employees, events, hr_profiles, absences)
    return build_worktime_overview(*scoped)["employees"]


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    employees, events, hr_profiles, absences = get_data()
    card = build_employee_card(employee_id, employees, events, hr_profiles, absences)

    if not card:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    return card


@app.get("/employees/{employee_id}/risk-explanation", response_model=RiskExplanation)
def get_employee_risk_explanation(employee_id: int):
    employees, events, hr_profiles, absences = get_data()
    explanation = build_risk_explanation(employee_id, employees, events, hr_profiles, absences)

    if not explanation:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    return explanation


@app.get("/analytics/summary")
def get_analytics_summary(department: str | None = None):
    employees, events, hr_profiles, absences = get_data()
    scoped = filter_by_department(department, employees, events, hr_profiles, absences)
    return build_summary(*scoped)


@app.get("/analytics/conflicts", response_model=list[Conflict])
def get_analytics_conflicts(department: str | None = None):
    employees, events, hr_profiles, absences = get_data()
    scoped_employees, scoped_events, _, _ = filter_by_department(department, employees, events, hr_profiles, absences)
    return build_conflicts(scoped_employees, scoped_events)


@app.get("/analytics/data-mismatches", response_model=list[DataMismatch])
def get_analytics_data_mismatches(department: str | None = None):
    employees, events, hr_profiles, absences = get_data()
    scoped_employees, _, scoped_hr_profiles, _ = filter_by_department(department, employees, events, hr_profiles, absences)
    return build_data_mismatches(scoped_employees, scoped_hr_profiles)


@app.get("/analytics/data-quality")
def get_analytics_data_quality():
    employees, events, hr_profiles, absences = get_data()
    return build_data_quality(employees, events, hr_profiles, absences, get_data_source_info())


@app.get("/analytics/availability", response_model=list[AvailabilityDay])
def get_analytics_availability(department: str | None = None):
    employees, events, hr_profiles, absences = get_data()
    scoped = filter_by_department(department, employees, events, hr_profiles, absences)
    return build_availability(*scoped)


@app.get("/analytics/groups")
def get_analytics_groups(department: str | None = None):
    employees, events, hr_profiles, absences = get_data()
    scoped = filter_by_department(department, employees, events, hr_profiles, absences)
    return build_groups(*scoped)


@app.get("/recommendations", response_model=list[Recommendation])
def get_recommendations(department: str | None = None):
    employees, events, hr_profiles, absences = get_data()
    scoped = filter_by_department(department, employees, events, hr_profiles, absences)
    return build_recommendations(*scoped)


@app.get("/notifications", response_model=list[Notification])
def get_notifications(department: str | None = None):
    employees, events, hr_profiles, absences = get_data()
    scoped = filter_by_department(department, employees, events, hr_profiles, absences)
    return build_notifications(*scoped)


@app.get("/meeting-slots", response_model=list[MeetingSlot])
def get_meeting_slots(department: str | None = None):
    employees, events, hr_profiles, absences = get_data()
    scoped = filter_by_department(department, employees, events, hr_profiles, absences)
    return build_best_slots(*scoped)


@app.post("/upload/{dataset}")
async def upload_dataset(dataset: str, file: UploadFile = File(...)):
    suffix = "." + file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""

    try:
        path = save_uploaded_table(dataset, suffix, await file.read())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "status": "uploaded",
        "dataset": dataset,
        "filename": path.name,
        "message": "Файл сохранён и проверен. Следующий запрос к API перечитает данные.",
    }
