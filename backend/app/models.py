from pydantic import BaseModel
from typing import List, Optional


class Employee(BaseModel):
    id: int
    name: str
    team: str
    role: str
    timezone: str
    work_start: str
    work_end: str
    work_days: List[str]
    work_format: str
    last_update_date: str


class Event(BaseModel):
    id: int
    employee_id: int
    title: str
    start_datetime: str
    end_datetime: str
    source: str
    type: str


class HRProfile(BaseModel):
    employee_id: int
    hr_timezone: str
    hr_work_format: str
    hr_work_start: str
    hr_work_end: str


class EmployeeMetrics(BaseModel):
    days_since_update: int
    schedule_actuality: float
    outside_work_events: int
    total_events: int
    outside_work_ratio: float
    busy_hours: float
    work_hours: float
    load: float
    timezone_mismatch: int
    hr_mismatch: int
    conflict_count: int
    risk: float
    risk_status: str


class EmployeeListItem(BaseModel):
    id: int
    name: str
    team: str
    role: str
    timezone: str
    work_format: str
    metrics: EmployeeMetrics


class EmployeeCard(BaseModel):
    employee: Employee
    hr_profile: Optional[HRProfile]
    events: List[Event]
    metrics: EmployeeMetrics
    recommendations: List[str]
