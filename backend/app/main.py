from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.analytics import build_employee_card, build_employee_list, build_summary
from app.data_loader import load_employees, load_events, load_hr_profiles

app = FastAPI(
    title="WorkTime Sync Backend",
    description="MVP backend для расчёта актуальности рабочих графиков сотрудников.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_data():
    """Для MVP перечитываем JSON при каждом запросе: удобно менять тестовые данные без БД."""
    employees = load_employees()
    events = load_events()
    hr_profiles = load_hr_profiles()
    return employees, events, hr_profiles


@app.get("/")
def root():
    return {
        "service": "WorkTime Sync Backend",
        "docs": "/docs",
        "endpoints": ["/employees", "/employees/{id}", "/analytics/summary"],
    }


@app.get("/employees")
def get_employees():
    employees, events, hr_profiles = get_data()
    return build_employee_list(employees, events, hr_profiles)


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    employees, events, hr_profiles = get_data()
    card = build_employee_card(employee_id, employees, events, hr_profiles)

    if not card:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    return card


@app.get("/analytics/summary")
def get_analytics_summary():
    employees, events, hr_profiles = get_data()
    return build_summary(employees, events, hr_profiles)
