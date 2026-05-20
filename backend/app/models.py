from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


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


class Absence(BaseModel):
    id: int
    employee_id: int
    type: str
    start_date: str
    end_date: str


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
    absence_count: int
    conflict_count: int
    risk: float
    risk_status: str
    risk_tone: str


class FrontendEmployee(BaseModel):
    id: int
    name: str
    role: str
    team: str
    format: str
    timezone: str
    workDays: List[str]
    workStart: int
    workEnd: int
    updatedAt: str
    meetingsTotal: int
    meetingsOutside: int
    busyHours: float
    workHours: float
    timezoneMismatch: int
    hrCalendarMismatch: int
    exceptions: List[str]
    statusNote: str
    metrics: EmployeeMetrics


class Recommendation(BaseModel):
    type: str
    title: str
    reason: str
    priority: str


class Conflict(BaseModel):
    id: int
    employeeId: int
    employee: str
    title: str
    day: str
    time: str
    reason: str
    severity: str
