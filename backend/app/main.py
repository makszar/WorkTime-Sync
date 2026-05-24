from __future__ import annotations
import json
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.analytics import build_availability, build_best_slots, build_company_analytics, build_conflicts, build_data_mismatches, build_employee_card, build_employee_list, build_groups, build_hr_dashboard, build_notifications, build_recommendations, build_risk_explanation, build_summary, build_worktime_overview, is_event_outside_work_time
from app.data_loader import get_data_source_info, get_schema_definitions, load_absences, load_employees, load_events, load_hr_profiles, load_schedule_confirmations, load_tasks, save_schedule_confirmations, save_tasks, save_uploaded_table
from app.data_quality import build_data_quality
from app.models import AvailabilityDay, Conflict, DataMismatch, MeetingSlot, Notification, Recommendation, RiskExplanation

PROJECT_ROOT=Path(__file__).resolve().parents[2]
USERS_PATH=PROJECT_ROOT/"data"/"synthetic"/"users.json"
ALLOWED_TASK_TYPES={"confirm_schedule","review_hr_profile","review_load","update_timezone","meeting_confirmation","reschedule_meeting","meeting_outside_work_approval"}
MEETING_TASK_TYPES={"meeting_confirmation","reschedule_meeting","meeting_outside_work_approval"}
ALLOWED_TASK_STATUSES={"pending","confirmed","rejected","done","expired","reschedule_requested"}
COMMENT_REQUIRED_STATUSES={"rejected","reschedule_requested"}
DEFAULT_USERS=[{"id":"u0","login":"executive_demo","password":"test0","name":"Executive Demo","role":"executive","role_label":"Полный руководитель","scope":"all","department":None,"employee_id":None},{"id":"u_hr","login":"hr_demo","password":"testhr","name":"HR Demo","role":"hr","role_label":"HR","scope":"all","department":None,"employee_id":None},{"id":"u1","login":"zarix","password":"i9VUibm6","name":"Зарубин Максим","role":"department_manager","role_label":"Руководитель отдела","scope":"department","department":"Core Platform","employee_id":None},{"id":"emp5","login":"gleb_employee","password":"emp5","name":"Глеб Соколов","role":"employee","role_label":"Сотрудник","scope":"self","department":"Core Platform","employee_id":5}]

class LoginRequest(BaseModel):
    login:str
    password:str
class TaskCreateRequest(BaseModel):
    employee_id:int
    type:str
    title:str
    description:str
    due_date:str
    related_event_id:int|None=None
    meeting_action:str|None=None
    suggested_start_datetime:str|None=None
    suggested_end_datetime:str|None=None
class TaskStatusRequest(BaseModel):
    status:str
    employee_comment:str=""
    suggested_start_datetime:str|None=None
    suggested_end_datetime:str|None=None
class ConfirmScheduleRequest(BaseModel):
    comment:str=""

app=FastAPI(title="WorkTime Sync Backend",description="FastAPI backend для WorkTime Sync: аналитика, роли, задачи и подтверждения.",version="2.3.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

def now_iso(): return datetime.now().isoformat(timespec="seconds")
def public_user(user): return {k:v for k,v in user.items() if k!="password"}
def load_users():
    if not USERS_PATH.exists(): return DEFAULT_USERS
    users=json.loads(USERS_PATH.read_text(encoding="utf-8"))
    if not isinstance(users,list): raise HTTPException(status_code=500,detail="users.json должен содержать список профилей")
    return users
def get_user(user_id): return next((u for u in load_users() if u.get("id")==user_id),None) if user_id else None
def require_user(user_id):
    user=get_user(user_id)
    if not user: raise HTTPException(status_code=401,detail="Неизвестный пользователь или не передан user_id")
    return user

def filter_by_department(department,employees,events,hr_profiles,absences):
    if not department: return employees,events,hr_profiles,absences
    scoped=[e for e in employees if e.get("team")==department]; ids={int(e["id"]) for e in scoped}
    return scoped,[e for e in events if int(e["employee_id"]) in ids],[p for p in hr_profiles if int(p["employee_id"]) in ids],[a for a in absences if int(a["employee_id"]) in ids]
def filter_by_employee_id(employee_id,employees,events,hr_profiles,absences):
    scoped=[e for e in employees if int(e["id"])==int(employee_id)]; ids={int(e["id"]) for e in scoped}
    return scoped,[e for e in events if int(e["employee_id"]) in ids],[p for p in hr_profiles if int(p["employee_id"]) in ids],[a for a in absences if int(a["employee_id"]) in ids]
def apply_user_scope(user,employees,events,hr_profiles,absences,department=None):
    if user:
        if user.get("role") in {"executive","hr"} or user.get("scope")=="all": return employees,events,hr_profiles,absences
        if user.get("role")=="department_manager" or user.get("scope")=="department": return filter_by_department(user.get("department"),employees,events,hr_profiles,absences)
        if user.get("role")=="employee" or user.get("scope")=="self": return filter_by_employee_id(int(user.get("employee_id") or 0),employees,events,hr_profiles,absences)
    return filter_by_department(department,employees,events,hr_profiles,absences)
def departments_from_employees(employees): return [{"name":t,"count":sum(1 for e in employees if e.get("team")==t)} for t in sorted({e.get("team") for e in employees if e.get("team")})]
def get_data():
    try: return load_employees(),load_events(),load_hr_profiles(),load_absences()
    except (FileNotFoundError,ValueError) as e: raise HTTPException(status_code=500,detail=str(e)) from e
def get_extended_data():
    employees,events,hr_profiles,absences=get_data()
    try: tasks=load_tasks(); confirmations=load_schedule_confirmations()
    except (FileNotFoundError,ValueError) as e: raise HTTPException(status_code=500,detail=str(e)) from e
    return employees,events,hr_profiles,absences,tasks,confirmations

def can_access_employee(user,employee):
    if user.get("role") in {"executive","hr"} or user.get("scope")=="all": return True
    if user.get("role")=="department_manager": return employee.get("team")==user.get("department")
    if user.get("role")=="employee": return int(employee["id"])==int(user.get("employee_id") or -1)
    return False
def can_view_task(user,task):
    if user.get("role") in {"executive","hr"} or user.get("scope")=="all": return True
    if user.get("role")=="department_manager": return task.get("department")==user.get("department")
    if user.get("role")=="employee": return int(task["employee_id"])==int(user.get("employee_id") or -1)
    return False
def can_create_task_for_employee(user,employee): return user.get("role") in {"executive","hr","department_manager"} and can_access_employee(user,employee)
def can_update_task(user,task,next_status):
    if user.get("role") in {"executive","hr"}: return True
    if user.get("role")=="department_manager": return task.get("department")==user.get("department")
    if user.get("role")=="employee": return int(task["employee_id"])==int(user.get("employee_id") or -1) and next_status in {"confirmed","rejected","reschedule_requested"}
    return False

def validate_datetime_range(start_value,end_value):
    if not start_value and not end_value: return
    if not start_value or not end_value: raise HTTPException(status_code=400,detail="Для переноса нужно передать suggested_start_datetime и suggested_end_datetime")
    try: start=datetime.fromisoformat(start_value); end=datetime.fromisoformat(end_value)
    except ValueError as e: raise HTTPException(status_code=400,detail=f"Некорректный datetime переноса: {e}") from e
    if end<=start: raise HTTPException(status_code=400,detail="suggested_end_datetime должен быть позже suggested_start_datetime")
def validate_task_payload(payload,employee,events):
    if payload.type not in ALLOWED_TASK_TYPES: raise HTTPException(status_code=400,detail=f"Неизвестный тип задачи: {payload.type}")
    if payload.type in MEETING_TASK_TYPES and payload.related_event_id is None: raise HTTPException(status_code=400,detail="Для задачи по встрече нужно передать related_event_id")
    event=None
    if payload.related_event_id is not None:
        event=next((e for e in events if int(e["id"])==int(payload.related_event_id)),None)
        if not event: raise HTTPException(status_code=400,detail="related_event_id не найден в events.csv")
        if int(event["employee_id"])!=int(payload.employee_id): raise HTTPException(status_code=400,detail="related_event_id относится к другому сотруднику")
    if payload.type=="meeting_outside_work_approval" and event and not is_event_outside_work_time(event,employee):
        raise HTTPException(status_code=400,detail="Событие не выходит за пределы рабочего времени")
    if payload.type=="reschedule_meeting": validate_datetime_range(payload.suggested_start_datetime,payload.suggested_end_datetime)
def users_by_id(): return {u["id"]:u for u in load_users()}
def enrich_task(task,employees_by_id,events_by_id,users_map):
    employee=employees_by_id.get(int(task["employee_id"])); creator=users_map.get(task.get("created_by_user_id"))
    related=task.get("related_event_id"); event=events_by_id.get(int(related)) if related not in (None,"") else None
    return {**task,"employee_name":employee.get("name") if employee else None,"employee_role":employee.get("role") if employee else None,"employee_team":employee.get("team") if employee else task.get("department"),"related_event":event,"creator_name":creator.get("name") if creator else task.get("created_by_user_id"),"creator_role_label":creator.get("role_label") if creator else task.get("created_by_role")}
def enrich_tasks(tasks,employees,events):
    return [enrich_task(t,{int(e["id"]):e for e in employees},{int(e["id"]):e for e in events},users_by_id()) for t in tasks]
def task_status_counts(tasks):
    counts=Counter(t.get("status") for t in tasks)
    return {s:counts.get(s,0) for s in sorted(ALLOWED_TASK_STATUSES)}
def tasks_by_department(tasks):
    rows=defaultdict(lambda:{"department":"","total":0,"pending":0,"rejected":0,"done":0})
    for t in tasks:
        row=rows[t["department"]]; row["department"]=t["department"]; row["total"]+=1
        if t.get("status") in row: row[t["status"]]+=1
    return sorted(rows.values(), key=lambda x:x["department"])
def confirmation_rate(employees,confirmations):
    confirmed={int(c["employee_id"]) for c in confirmations if c.get("status")=="confirmed"}
    return round(len(confirmed)/len(employees),2) if employees else 0
def confirmation_stats_by_department(employees,confirmations):
    status={int(c["employee_id"]):c.get("status") for c in confirmations}; rows=[]
    for dep in sorted({e["team"] for e in employees}):
        em=[e for e in employees if e["team"]==dep]; confirmed=sum(1 for e in em if status.get(int(e["id"]))=="confirmed")
        rows.append({"department":dep,"employees":len(em),"confirmed":confirmed,"confirmationRate":round(confirmed/len(em),2) if em else 0})
    return rows
def conflicting_events_for_employee(employee,events): return [e for e in events if int(e["employee_id"])==int(employee["id"]) and is_event_outside_work_time(e,employee)]

@app.post("/auth/login")
def login(payload:LoginRequest):
    user=next((u for u in load_users() if u.get("login")==payload.login.strip() and u.get("password")==payload.password),None)
    if not user: raise HTTPException(status_code=401,detail="Неверный логин или пароль")
    return {"token":f"demo-{user['login']}","user":public_user(user)}
@app.get("/")
def root(): return {"service":"WorkTime Sync Backend","docs":"/docs","version":app.version,"frontend_endpoint":"/api/worktime/overview","auth_endpoint":"/auth/login"}
@app.get("/health")
def healthcheck(): return {"status":"ok"}
@app.get("/health/data")
def health_data():
    e,ev,hr,a,t,c=get_extended_data(); src=get_data_source_info()
    return {"status":"ok","data_source":src["active_source"],"employees":len(e),"events":len(ev),"hr_profiles":len(hr),"absences":len(a),"tasks":len(t),"schedule_confirmations":len(c),"datasets":src["datasets"]}
@app.get("/data/source")
def get_data_source(): return get_data_source_info()
@app.get("/schemas")
def get_schemas(): return get_schema_definitions()
@app.get("/api/worktime/overview")
def get_worktime_overview(department:str|None=None,user_id:str|None=None):
    e,ev,hr,a,t,c=get_extended_data(); user=get_user(user_id); scoped=apply_user_scope(user,e,ev,hr,a,department); result=build_worktime_overview(*scoped)
    ids={int(x["id"]) for x in scoped[0]}; scoped_tasks=[x for x in t if int(x["employee_id"]) in ids]; src=get_data_source_info()
    result.update({"tasks":enrich_tasks(scoped_tasks,e,ev),"taskStatusCounts":task_status_counts(scoped_tasks),"total_synthetic_employees":len(e),"departments":departments_from_employees(e),"currentUser":public_user(user) if user else None,"meta":{"backend_version":app.version,"data_source":src["active_source"],"department":department,"user_id":user_id,"scope":user.get("scope") if user else None,"role":user.get("role") if user else None,"employees_count":len(scoped[0]),"events_count":len(scoped[1]),"hr_profiles_count":len(scoped[2]),"absences_count":len(scoped[3]),"tasks_count":len(scoped_tasks),"total_employees_count":len(e),"generated_at":datetime.now().isoformat(timespec="seconds")}})
    return result
@app.get("/employees")
def get_employees(department:str|None=None,user_id:str|None=None):
    e,ev,hr,a=get_data(); return build_employee_list(*apply_user_scope(get_user(user_id),e,ev,hr,a,department))
@app.get("/employees/frontend")
def get_frontend_employees(department:str|None=None,user_id:str|None=None):
    e,ev,hr,a=get_data(); return build_worktime_overview(*apply_user_scope(get_user(user_id),e,ev,hr,a,department))["employees"]
@app.get("/employees/me")
def get_my_employee(user_id:str):
    user=require_user(user_id)
    if user.get("role")!="employee": raise HTTPException(status_code=403,detail="Личный кабинет доступен только роли employee")
    e,ev,hr,a,t,c=get_extended_data(); eid=int(user.get("employee_id") or 0); employee=next((x for x in e if int(x["id"])==eid),None)
    if not employee: raise HTTPException(status_code=404,detail="Сотрудник не найден")
    card=build_employee_card(eid,e,ev,hr,a); employee_tasks=[x for x in t if int(x["employee_id"])==eid]; enriched=enrich_tasks(employee_tasks,e,ev)
    card["tasks"]=enriched; card["pendingTasks"]=[x for x in enriched if x["status"]=="pending"]; card["completedTasks"]=[x for x in enriched if x["status"] in {"confirmed","done","expired"}]; card["tasksByType"]=dict(Counter(x["type"] for x in enriched)); card["meetingTasks"]=[x for x in enriched if x["type"] in MEETING_TASK_TYPES]; card["upcomingEvents"]=[x for x in ev if int(x["employee_id"])==eid]; card["conflictingEvents"]=conflicting_events_for_employee(employee,ev); card["scheduleConfirmationStatus"]=next((x.get("status") for x in c if int(x["employee_id"])==eid),"not_confirmed")
    return card
@app.get("/employees/{employee_id}")
def get_employee(employee_id:int,user_id:str|None=None):
    e,ev,hr,a=get_data(); emp=next((x for x in e if int(x["id"])==employee_id),None)
    if not emp: raise HTTPException(status_code=404,detail="Сотрудник не найден")
    user=get_user(user_id)
    if user and not can_access_employee(user,emp): raise HTTPException(status_code=403,detail="Нет доступа к этому сотруднику")
    return build_employee_card(employee_id,e,ev,hr,a)
@app.get("/employees/{employee_id}/risk-explanation",response_model=RiskExplanation)
def get_employee_risk_explanation(employee_id:int,user_id:str|None=None):
    e,ev,hr,a,_,c=get_extended_data(); emp=next((x for x in e if int(x["id"])==employee_id),None)
    if not emp: raise HTTPException(status_code=404,detail="Сотрудник не найден")
    user=get_user(user_id)
    if user and not can_access_employee(user,emp): raise HTTPException(status_code=403,detail="Нет доступа к этому сотруднику")
    return build_risk_explanation(employee_id,e,ev,hr,a,c)
@app.patch("/employees/{employee_id}/confirm-schedule")
def confirm_employee_schedule(employee_id:int,payload:ConfirmScheduleRequest,user_id:str):
    user=require_user(user_id); e,ev,hr,a,t,c=get_extended_data(); emp=next((x for x in e if int(x["id"])==employee_id),None)
    if not emp: raise HTTPException(status_code=404,detail="Сотрудник не найден")
    if not can_access_employee(user,emp): raise HTTPException(status_code=403,detail="Нет доступа к подтверждению графика")
    ts=now_iso(); record={"employee_id":employee_id,"confirmed_by_user_id":user["id"],"confirmed_at":ts,"comment":payload.comment,"status":"confirmed","updated_at":ts}; old=next((x for x in c if int(x["employee_id"])==employee_id),None)
    if old: old.update(record)
    else: c.append(record)
    for task in t:
        if int(task["employee_id"])==employee_id and task.get("type")=="confirm_schedule" and task.get("status")=="pending": task["status"]="confirmed"; task["employee_comment"]=payload.comment; task["updated_at"]=ts
    save_schedule_confirmations(c); save_tasks(t); return record
@app.get("/analytics/summary")
def get_analytics_summary(department:str|None=None,user_id:str|None=None):
    e,ev,hr,a=get_data(); return build_summary(*apply_user_scope(get_user(user_id),e,ev,hr,a,department))
@app.get("/analytics/company")
def get_analytics_company(user_id:str):
    user=require_user(user_id)
    if user.get("role") not in {"executive","hr"}: raise HTTPException(status_code=403,detail="Company analytics доступны только executive или HR")
    e,ev,hr,a,t,c=get_extended_data(); result=build_company_analytics(e,ev,hr,a); conflicts=build_conflicts(e,ev); conflict_counts=Counter(next((emp["team"] for emp in e if int(emp["id"])==int(x["employeeId"])),"unknown") for x in conflicts)
    result.update({"tasksByDepartment":tasks_by_department(t),"taskStatusCounts":task_status_counts(t),"pendingTasks":sum(1 for x in t if x["status"]=="pending"),"rejectedTasks":sum(1 for x in t if x["status"]=="rejected"),"scheduleConfirmationRate":confirmation_rate(e,c),"confirmationByDepartment":confirmation_stats_by_department(e,c),"worstConfirmationDepartments":sorted(confirmation_stats_by_department(e,c),key=lambda x:x["confirmationRate"])[:3],"outsideWorkMeetingDepartments":[{"department":dep,"outsideWorkMeetings":cnt} for dep,cnt in sorted(conflict_counts.items())]})
    return result
@app.get("/analytics/hr-dashboard")
def get_hr_dashboard(user_id:str):
    user=require_user(user_id)
    if user.get("role") not in {"hr","executive"}: raise HTTPException(status_code=403,detail="HR dashboard доступен только HR или executive")
    e,ev,hr,a,t,c=get_extended_data(); result=build_hr_dashboard(e,ev,hr,a,t,c); today=date(2026,5,19)
    result.update({"pendingTasks":enrich_tasks([x for x in t if x["status"]=="pending"],e,ev),"rejectedTasks":enrich_tasks([x for x in t if x["status"]=="rejected"],e,ev),"overdueTasks":enrich_tasks([x for x in t if x["status"]=="pending" and date.fromisoformat(x["due_date"])<today],e,ev),"changeRequestedConfirmations":[x for x in c if x.get("status")=="change_requested"],"confirmationByDepartment":confirmation_stats_by_department(e,c),"taskStatusCounts":task_status_counts(t)})
    return result
@app.get("/analytics/conflicts",response_model=list[Conflict])
def get_analytics_conflicts(department:str|None=None,user_id:str|None=None):
    e,ev,hr,a=get_data(); se,sev,_,_=apply_user_scope(get_user(user_id),e,ev,hr,a,department); return build_conflicts(se,sev)
@app.get("/analytics/data-mismatches",response_model=list[DataMismatch])
def get_analytics_data_mismatches(department:str|None=None,user_id:str|None=None):
    e,ev,hr,a=get_data(); se,_,shr,_=apply_user_scope(get_user(user_id),e,ev,hr,a,department); return build_data_mismatches(se,shr)
@app.get("/analytics/data-quality")
def get_analytics_data_quality():
    e,ev,hr,a,t,c=get_extended_data(); return build_data_quality(e,ev,hr,a,get_data_source_info(),t,c)
@app.get("/analytics/availability",response_model=list[AvailabilityDay])
def get_analytics_availability(department:str|None=None,user_id:str|None=None):
    e,ev,hr,a=get_data(); return build_availability(*apply_user_scope(get_user(user_id),e,ev,hr,a,department))
@app.get("/analytics/groups")
def get_analytics_groups(department:str|None=None,user_id:str|None=None):
    e,ev,hr,a=get_data(); return build_groups(*apply_user_scope(get_user(user_id),e,ev,hr,a,department))
@app.get("/recommendations",response_model=list[Recommendation])
def get_recommendations(department:str|None=None,user_id:str|None=None):
    e,ev,hr,a=get_data(); return build_recommendations(*apply_user_scope(get_user(user_id),e,ev,hr,a,department))
@app.get("/notifications",response_model=list[Notification])
def get_notifications(department:str|None=None,user_id:str|None=None):
    e,ev,hr,a=get_data(); return build_notifications(*apply_user_scope(get_user(user_id),e,ev,hr,a,department))
@app.get("/meeting-slots",response_model=list[MeetingSlot])
def get_meeting_slots(department:str|None=None,user_id:str|None=None):
    e,ev,hr,a=get_data(); return build_best_slots(*apply_user_scope(get_user(user_id),e,ev,hr,a,department))
@app.get("/tasks")
def get_tasks(user_id:str,status:str|None=None,department:str|None=None):
    user=require_user(user_id); e,ev,_,_,t,_=get_extended_data(); visible=[x for x in t if can_view_task(user,x)]
    if status: visible=[x for x in visible if x.get("status")==status]
    if department: visible=[x for x in visible if x.get("department")==department]
    return enrich_tasks(visible,e,ev)
@app.get("/tasks/my")
def get_my_tasks(user_id:str):
    user=require_user(user_id)
    if user.get("role")!="employee": raise HTTPException(status_code=403,detail="/tasks/my доступен только сотрудникам")
    e,ev,_,_,t,_=get_extended_data(); my=[x for x in t if int(x["employee_id"])==int(user.get("employee_id") or 0)]
    return enrich_tasks(my,e,ev)
@app.post("/tasks")
def create_task(payload:TaskCreateRequest,user_id:str):
    user=require_user(user_id); e,ev,_,_=get_data(); emp=next((x for x in e if int(x["id"])==payload.employee_id),None)
    if not emp: raise HTTPException(status_code=404,detail="Сотрудник не найден")
    if not can_create_task_for_employee(user,emp): raise HTTPException(status_code=403,detail="Нет прав создать задачу этому сотруднику")
    validate_task_payload(payload,emp,ev); t=load_tasks(); ts=now_iso(); task={"id":max([int(x["id"]) for x in t],default=0)+1,"employee_id":payload.employee_id,"created_by_user_id":user["id"],"created_by_role":user["role"],"department":emp["team"],"type":payload.type,"title":payload.title,"description":payload.description,"due_date":payload.due_date,"status":"pending","employee_comment":"","created_at":ts,"updated_at":ts,"related_event_id":payload.related_event_id,"meeting_action":payload.meeting_action,"suggested_start_datetime":payload.suggested_start_datetime,"suggested_end_datetime":payload.suggested_end_datetime}
    t.append(task); save_tasks(t); return enrich_tasks([task],e,ev)[0]
@app.get("/tasks/{task_id}")
def get_task(task_id:int,user_id:str):
    user=require_user(user_id); e,ev,_,_,t,_=get_extended_data(); task=next((x for x in t if int(x["id"])==task_id),None)
    if not task: raise HTTPException(status_code=404,detail="Задача не найдена")
    if not can_view_task(user,task): raise HTTPException(status_code=403,detail="Нет доступа к задаче")
    return enrich_tasks([task],e,ev)[0]
@app.patch("/tasks/{task_id}/status")
def update_task_status(task_id:int,payload:TaskStatusRequest,user_id:str):
    user=require_user(user_id); e,ev,_,_,t,_=get_extended_data(); task=next((x for x in t if int(x["id"])==task_id),None)
    if not task: raise HTTPException(status_code=404,detail="Задача не найдена")
    if payload.status not in ALLOWED_TASK_STATUSES: raise HTTPException(status_code=400,detail=f"Неизвестный статус задачи: {payload.status}")
    if payload.status in COMMENT_REQUIRED_STATUSES and not payload.employee_comment.strip(): raise HTTPException(status_code=400,detail="Для rejected/reschedule_requested комментарий обязателен")
    if payload.status=="reschedule_requested": validate_datetime_range(payload.suggested_start_datetime,payload.suggested_end_datetime)
    if not can_update_task(user,task,payload.status): raise HTTPException(status_code=403,detail="Нет прав изменить статус задачи")
    task["status"]=payload.status; task["employee_comment"]=payload.employee_comment
    if payload.suggested_start_datetime is not None: task["suggested_start_datetime"]=payload.suggested_start_datetime
    if payload.suggested_end_datetime is not None: task["suggested_end_datetime"]=payload.suggested_end_datetime
    task["updated_at"]=now_iso(); save_tasks(t); return enrich_tasks([task],e,ev)[0]
@app.post("/upload/{dataset}")
async def upload_dataset(dataset:str,file:UploadFile=File(...)):
    suffix="."+file.filename.rsplit(".",1)[-1].lower() if file.filename and "." in file.filename else ""
    try: path=save_uploaded_table(dataset,suffix,await file.read())
    except ValueError as e: raise HTTPException(status_code=400,detail=str(e)) from e
    return {"status":"uploaded","dataset":dataset,"filename":path.name,"message":"Файл сохранён и проверен. Следующий запрос к API перечитает данные."}
