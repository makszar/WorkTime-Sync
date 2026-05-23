from __future__ import annotations
from typing import Any, List, Literal
from pydantic import BaseModel

class Employee(BaseModel):
    id:int; name:str; team:str; role:str; timezone:str; work_start:str; work_end:str; work_days:List[str]; work_format:str; last_update_date:str
class Event(BaseModel):
    id:int; employee_id:int; title:str; start_datetime:str; end_datetime:str; source:str; type:str
class Absence(BaseModel):
    id:int; employee_id:int; type:str; start_date:str; end_date:str
class HRProfile(BaseModel):
    employee_id:int; hr_timezone:str; hr_work_format:str; hr_work_start:str; hr_work_end:str
class UserProfile(BaseModel):
    id:str; login:str; password:str; name:str; role:Literal['executive','department_manager','hr','employee']; scope:Literal['all','department','self']; role_label:str|None=None; department:str|None=None; employee_id:int|None=None
class Task(BaseModel):
    id:int; employee_id:int; created_by_user_id:str; created_by_role:str; department:str; type:Literal['confirm_schedule','review_hr_profile','reschedule_meeting','review_load','update_timezone']; title:str; description:str; due_date:str; status:Literal['pending','confirmed','rejected','done','expired']; employee_comment:str=''; created_at:str; updated_at:str
class ScheduleConfirmation(BaseModel):
    employee_id:int; confirmed_by_user_id:str=''; confirmed_at:str=''; comment:str=''; status:Literal['not_confirmed','pending','confirmed','rejected']='not_confirmed'; updated_at:str=''
class EmployeeMetrics(BaseModel):
    days_since_update:int; schedule_actuality:float; outside_work_events:int; total_events:int; outside_work_ratio:float; busy_hours:float; work_hours:float; load:float; timezone_mismatch:int; hr_mismatch:int; absence_count:int; calendar_conflict_count:int; data_mismatch_count:int; issue_count:int; conflict_count:int; risk:float; risk_status:str; risk_tone:str; risk_weights:dict[str,float]|None=None; risk_formula:str|None=None; department_logic:str|None=None
class FrontendEmployee(BaseModel):
    id:int; name:str; role:str; team:str; format:str; timezone:str; workDays:List[str]; workStart:int; workEnd:int; updatedAt:str; meetingsTotal:int; meetingsOutside:int; busyHours:float; workHours:float; timezoneMismatch:int; hrCalendarMismatch:int; exceptions:List[str]; statusNote:str; metrics:EmployeeMetrics
class Recommendation(BaseModel):
    type:str; title:str; reason:str; priority:str; suggestedTaskType:str|None=None; targetEmployeeId:int|None=None; targetRole:str|None=None
class Conflict(BaseModel):
    id:int; employeeId:int; employee:str; title:str; day:str; time:str; reason:str; severity:str; source:str|None=None; type:str|None=None
class DataMismatch(BaseModel):
    id:str; employeeId:int; employee:str; type:str; title:str; reason:str; severity:str
class AvailabilitySlot(BaseModel):
    hour:int; count:int; type:str; missing:List[str]; missingDetails:List[dict[str,Any]]=[]
class AvailabilityDay(BaseModel):
    day:str; slots:List[AvailabilitySlot]
class MeetingSlot(BaseModel):
    label:str; count:int; missing:List[str]; missingDetails:List[dict[str,Any]]=[]
class Notification(BaseModel):
    id:str; recipientRole:str; employeeId:int|None=None; employee:str|None=None; title:str; reason:str; priority:str; action:str; suggestedTaskType:str|None=None
class RiskFactor(BaseModel):
    factor:str; label:str; value:Any; score:float; weightedScore:float|None=None; weight:float|None=None; impact:str; explanation:str
class RiskExplanation(BaseModel):
    employeeId:int; employee:str; department:str|None=None; risk:float; riskStatus:str; formula:str; weights:dict[str,float]|None=None; departmentLogic:str|None=None; formulaWithWeights:str|None=None; scheduleConfirmationStatus:str|None=None; factors:List[RiskFactor]; recommendedActions:List[str]
class GroupsResponse(BaseModel):
    actual:List[FrontendEmployee]; outdated:List[FrontendEmployee]; outsideWorkMeetings:List[FrontendEmployee]; highLoad:List[FrontendEmployee]; timezoneConflict:List[FrontendEmployee]; hrMismatch:List[FrontendEmployee]; needsConfirmation:List[FrontendEmployee]
