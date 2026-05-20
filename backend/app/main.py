from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

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
    load_absences,
    load_employees,
    load_events,
    load_hr_profiles,
    save_uploaded_table,
)
from app.models import AvailabilityDay, Conflict, DataMismatch, MeetingSlot, Notification, Recommendation, RiskExplanation

app = FastAPI(
    title="WorkTime Sync Backend",
    description="FastAPI backend для фронтенда WorkTime Sync и аналитики рабочего времени.",
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/")
def root():
    return {
        "service": "WorkTime Sync Backend",
        "docs": "/docs",
        "frontend_endpoint": "/api/worktime/overview",
        "endpoints": [
            "/api/worktime/overview",
            "/employees",
            "/employees/{employee_id}",
            "/employees/{employee_id}/risk-explanation",
            "/analytics/summary",
            "/analytics/conflicts",
            "/analytics/data-mismatches",
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


@app.get("/api/worktime/overview")
def get_worktime_overview():
    employees, events, hr_profiles, absences = get_data()
    return build_worktime_overview(employees, events, hr_profiles, absences)


@app.get("/employees")
def get_employees():
    employees, events, hr_profiles, absences = get_data()
    return build_employee_list(employees, events, hr_profiles, absences)


@app.get("/employees/frontend")
def get_frontend_employees():
    employees, events, hr_profiles, absences = get_data()
    return build_worktime_overview(employees, events, hr_profiles, absences)["employees"]


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
def get_analytics_summary():
    employees, events, hr_profiles, absences = get_data()
    return build_summary(employees, events, hr_profiles, absences)


@app.get("/analytics/conflicts", response_model=list[Conflict])
def get_analytics_conflicts():
    employees, events, _, _ = get_data()
    return build_conflicts(employees, events)


@app.get("/analytics/data-mismatches", response_model=list[DataMismatch])
def get_analytics_data_mismatches():
    employees, _, hr_profiles, _ = get_data()
    return build_data_mismatches(employees, hr_profiles)


@app.get("/analytics/availability", response_model=list[AvailabilityDay])
def get_analytics_availability():
    employees, events, hr_profiles, absences = get_data()
    return build_availability(employees, events, hr_profiles, absences)


@app.get("/analytics/groups")
def get_analytics_groups():
    employees, events, hr_profiles, absences = get_data()
    return build_groups(employees, events, hr_profiles, absences)


@app.get("/recommendations", response_model=list[Recommendation])
def get_recommendations():
    employees, events, hr_profiles, absences = get_data()
    return build_recommendations(employees, events, hr_profiles, absences)


@app.get("/notifications", response_model=list[Notification])
def get_notifications():
    employees, events, hr_profiles, absences = get_data()
    return build_notifications(employees, events, hr_profiles, absences)


@app.get("/meeting-slots", response_model=list[MeetingSlot])
def get_meeting_slots():
    employees, events, hr_profiles, absences = get_data()
    return build_best_slots(employees, events, hr_profiles, absences)


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
