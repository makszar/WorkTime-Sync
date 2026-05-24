from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.data_loader import load_events
from app.main import app
client=TestClient(app)
@pytest.fixture()
def isolated_data(monkeypatch,tmp_path:Path):
    monkeypatch.setenv('WORKTIME_DATA_DIR',str(tmp_path))
    (tmp_path/'employees.csv').write_text('id,name,team,role,timezone,work_start,work_end,work_days,work_format,last_update_date\nemp005,Глеб Соколов,Core Platform,Backend Engineer,Europe/Moscow,09:00,18:00,Mon|Tue|Wed|Thu|Fri,remote,2026-05-01\nemp012,Виктория Ершова,People Ops,HR Specialist,Europe/Moscow,09:00,18:00,Mon|Tue|Wed|Thu|Fri,hybrid,2026-05-01\n',encoding='utf-8')
    (tmp_path/'events.csv').write_text('id,employee_id,title,start_datetime,end_datetime,source,type\nevt001,emp005,Late sync,2026-05-20T18:30:00,2026-05-20T19:00:00,calendar,meeting\nevt002,emp012,HR sync,2026-05-20T10:00:00,2026-05-20T11:00:00,calendar,meeting\n',encoding='utf-8')
    (tmp_path/'hr_profiles.csv').write_text('employee_id,hr_timezone,hr_work_format,hr_work_start,hr_work_end\nemp005,Europe/Moscow,remote,09:00,18:00\nemp012,Europe/Moscow,hybrid,09:00,18:00\n',encoding='utf-8')
    (tmp_path/'absences.csv').write_text('id,employee_id,type,start_date,end_date\n',encoding='utf-8')
    (tmp_path/'tasks.json').write_text('''[{"id":1,"employee_id":5,"created_by_user_id":"u1","created_by_role":"department_manager","department":"Core Platform","type":"reschedule_meeting","title":"Перенести позднюю встречу","description":"Встреча вне рабочего времени.","due_date":"2026-05-24","status":"confirmed","employee_comment":"Согласен на перенос.","created_at":"2026-05-19T10:00:00","updated_at":"2026-05-20T10:00:00","related_event_id":1,"meeting_action":"reschedule","suggested_start_datetime":"2026-05-20T15:00:00","suggested_end_datetime":"2026-05-20T15:30:00","history":[]}]''',encoding='utf-8')
    (tmp_path/'schedule_confirmations.json').write_text('[]',encoding='utf-8')
    return tmp_path
def test_apply_reschedule_changes_event_and_closes_task(isolated_data):
    r=client.post('/tasks/1/apply?user_id=u1',json={})
    assert r.status_code==200
    data=r.json(); assert data['status']=='applied'; assert data['task']['status']=='done'; assert data['updated_event']['start_datetime']=='2026-05-20T15:00:00'
    event=next(x for x in load_events() if x['id']==1); assert event['start_datetime']=='2026-05-20T15:00:00'; assert event['end_datetime']=='2026-05-20T15:30:00'
def test_employee_cannot_apply_task(isolated_data):
    assert client.post('/tasks/1/apply?user_id=emp5',json={}).status_code==403
def test_generate_tasks_from_conflicts(isolated_data):
    r=client.post('/tasks/generate-from-conflicts?user_id=u1',json={'limit':1})
    assert r.status_code==200; assert r.json()['created']==0
def test_task_status_history_is_written(isolated_data):
    r=client.patch('/tasks/1/status?user_id=emp5',json={'status':'reschedule_requested','employee_comment':'Могу в 16:00.','suggested_start_datetime':'2026-05-20T16:00:00','suggested_end_datetime':'2026-05-20T16:30:00'})
    assert r.status_code==200; data=r.json(); assert data['history']; assert data['history'][-1]['new_status']=='reschedule_requested'
def test_data_quality_reports_task_workflow_errors(isolated_data):
    (isolated_data/'tasks.json').write_text('''[{"id":1,"employee_id":5,"created_by_user_id":"missing-user","created_by_role":"department_manager","department":"Core Platform","type":"reschedule_meeting","title":"Broken task","description":"Broken","due_date":"2026-05-24","status":"rejected","employee_comment":"","created_at":"2026-05-19T10:00:00","updated_at":"2026-05-20T10:00:00","related_event_id":999,"meeting_action":"reschedule","suggested_start_datetime":"","suggested_end_datetime":"","history":[]}]''',encoding='utf-8')
    r=client.get('/analytics/data-quality')
    assert r.status_code==200
    q=r.json(); assert q['status']=='error'; assert q['tasks_without_creator']; assert q['orphan_related_event_id']; assert q['reschedule_without_suggested_time']; assert q['rejected_without_comment']
