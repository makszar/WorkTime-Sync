from __future__ import annotations
from collections import Counter
from datetime import date, datetime
from typing import Any, Dict, List
ALLOWED_TASK_TYPES={"confirm_schedule","review_hr_profile","review_load","update_timezone","meeting_confirmation","reschedule_meeting","meeting_outside_work_approval"}
MEETING_TASK_TYPES={"meeting_confirmation","reschedule_meeting","meeting_outside_work_approval"}
ALLOWED_TASK_STATUSES={"pending","confirmed","rejected","done","expired","reschedule_requested"}
ALLOWED_CONFIRMATION_STATUSES={"not_confirmed","pending","confirmed","rejected","change_requested"}
def _duplicates(values:list[int])->list[int]:
    c=Counter(values); return sorted([v for v,n in c.items() if n>1])
def _is_empty(v): return v is None or v==''
def _invalid_datetime_range(s,e):
    if _is_empty(s) or _is_empty(e): return 'missing_suggested_time'
    try: start=datetime.fromisoformat(str(s)); end=datetime.fromisoformat(str(e))
    except ValueError as err: return f'invalid_datetime: {err}'
    if end<=start: return 'suggested_end_datetime должен быть позже suggested_start_datetime'
    return None
def build_data_quality(employees,events,hr_profiles,absences,source_info=None,tasks=None,schedule_confirmations=None,users=None):
    tasks=tasks or []; schedule_confirmations=schedule_confirmations or []; users=users or []
    employee_ids={int(e['id']) for e in employees}; event_by_id={int(e['id']):e for e in events}; event_ids=list(event_by_id.keys()); absence_ids=[int(a['id']) for a in absences]; task_ids=[int(t['id']) for t in tasks]; confirmation_employee_ids=[int(c['employee_id']) for c in schedule_confirmations]; hr_ids={int(p['employee_id']) for p in hr_profiles}; user_ids={u['id'] for u in users}
    orphan_events=[{'event_id':int(e['id']),'employee_id':int(e['employee_id']),'title':e.get('title','')} for e in events if int(e['employee_id']) not in employee_ids]
    orphan_absences=[{'absence_id':int(a['id']),'employee_id':int(a['employee_id']),'type':a.get('type','')} for a in absences if int(a['employee_id']) not in employee_ids]
    orphan_tasks=[{'task_id':int(t['id']),'employee_id':int(t['employee_id']),'title':t.get('title','')} for t in tasks if int(t['employee_id']) not in employee_ids]
    orphan_confirmations=[{'employee_id':int(c['employee_id']),'status':c.get('status','')} for c in schedule_confirmations if int(c['employee_id']) not in employee_ids]
    orphan_hr_profiles=[{'employee_id':int(p['employee_id'])} for p in hr_profiles if int(p['employee_id']) not in employee_ids]
    employees_without_hr_profile=[{'employee_id':int(e['id']),'name':e.get('name',''),'team':e.get('team','')} for e in employees if int(e['id']) not in hr_ids]
    tasks_without_creator=[]; meeting_task_without_related_event_id=[]; orphan_related_event_id=[]; task_event_mismatch=[]; invalid_task_types=[]; invalid_task_statuses=[]; reschedule_without_suggested_time=[]; rejected_without_comment=[]; reschedule_requested_without_comment=[]
    for t in tasks:
        tid=int(t['id']); typ=t.get('type'); st=t.get('status')
        if users and t.get('created_by_user_id') not in user_ids: tasks_without_creator.append({'task_id':tid,'created_by_user_id':t.get('created_by_user_id')})
        if typ not in ALLOWED_TASK_TYPES: invalid_task_types.append({'task_id':tid,'type':typ})
        if st not in ALLOWED_TASK_STATUSES: invalid_task_statuses.append({'task_id':tid,'status':st})
        if typ in MEETING_TASK_TYPES and _is_empty(t.get('related_event_id')): meeting_task_without_related_event_id.append({'task_id':tid,'type':typ})
        related=t.get('related_event_id')
        if not _is_empty(related):
            related=int(related); event=event_by_id.get(related)
            if not event: orphan_related_event_id.append({'task_id':tid,'related_event_id':related})
            elif int(event['employee_id'])!=int(t['employee_id']): task_event_mismatch.append({'task_id':tid,'related_event_id':related,'task_employee_id':int(t['employee_id']),'event_employee_id':int(event['employee_id'])})
        if typ=='reschedule_meeting' or st=='reschedule_requested':
            err=_invalid_datetime_range(t.get('suggested_start_datetime'),t.get('suggested_end_datetime'))
            if err: reschedule_without_suggested_time.append({'task_id':tid,'reason':err})
        if st=='rejected' and not str(t.get('employee_comment','')).strip(): rejected_without_comment.append({'task_id':tid})
        if st=='reschedule_requested' and not str(t.get('employee_comment','')).strip(): reschedule_requested_without_comment.append({'task_id':tid})
    invalid_confirmation_statuses=[{'employee_id':int(c['employee_id']),'status':c.get('status')} for c in schedule_confirmations if c.get('status') not in ALLOWED_CONFIRMATION_STATUSES]
    invalid_event_ranges=[]
    for e in events:
        try:
            if datetime.fromisoformat(e['end_datetime'])<=datetime.fromisoformat(e['start_datetime']): invalid_event_ranges.append({'event_id':int(e['id']),'title':e.get('title',''),'reason':'end_datetime должен быть позже start_datetime'})
        except ValueError as err: invalid_event_ranges.append({'event_id':int(e['id']),'title':e.get('title',''),'reason':f'Некорректный datetime: {err}'})
    invalid_absence_ranges=[]
    for a in absences:
        try:
            if date.fromisoformat(a['end_date'])<date.fromisoformat(a['start_date']): invalid_absence_ranges.append({'absence_id':int(a['id']),'employee_id':int(a['employee_id']),'reason':'end_date должен быть не раньше start_date'})
        except ValueError as err: invalid_absence_ranges.append({'absence_id':int(a['id']),'employee_id':int(a['employee_id']),'reason':f'Некорректная дата: {err}'})
    warnings=[]
    if orphan_hr_profiles: warnings.append('Есть HR-профили для сотрудников, которых нет в employees.')
    if employees_without_hr_profile: warnings.append('Есть сотрудники без HR-профиля.')
    if len(hr_profiles)!=len(employees): warnings.append('Количество HR-профилей отличается от количества сотрудников.')
    if orphan_tasks: warnings.append('Есть задачи для сотрудников, которых нет в employees.')
    if orphan_confirmations: warnings.append('Есть подтверждения графика для сотрудников, которых нет в employees.')
    blocking=(orphan_events or orphan_absences or invalid_event_ranges or invalid_absence_ranges or orphan_related_event_id or task_event_mismatch or invalid_task_types or invalid_task_statuses or invalid_confirmation_statuses or tasks_without_creator or meeting_task_without_related_event_id or reschedule_without_suggested_time or rejected_without_comment or reschedule_requested_without_comment or _duplicates([int(e['id']) for e in employees]) or _duplicates(event_ids) or _duplicates(absence_ids) or _duplicates(task_ids) or _duplicates(confirmation_employee_ids))
    return {'status':'warning' if warnings and not blocking else ('error' if blocking else 'ok'),'source':(source_info or {}).get('active_source'),'employees':len(employees),'events':len(events),'hr_profiles':len(hr_profiles),'absences':len(absences),'tasks':len(tasks),'schedule_confirmations':len(schedule_confirmations),'teams':sorted({e.get('team','') for e in employees if e.get('team')}),'duplicate_employee_ids':_duplicates([int(e['id']) for e in employees]),'duplicate_event_ids':_duplicates(event_ids),'duplicate_absence_ids':_duplicates(absence_ids),'duplicate_task_ids':_duplicates(task_ids),'duplicate_confirmations':_duplicates(confirmation_employee_ids),'orphan_events':orphan_events,'orphan_absences':orphan_absences,'orphan_tasks':orphan_tasks,'orphan_confirmations':orphan_confirmations,'tasks_without_creator':tasks_without_creator,'meeting_task_without_related_event_id':meeting_task_without_related_event_id,'orphan_related_event_id':orphan_related_event_id,'task_event_mismatch':task_event_mismatch,'orphan_hr_profiles':orphan_hr_profiles,'employees_without_hr_profile':employees_without_hr_profile,'invalid_event_ranges':invalid_event_ranges,'invalid_absence_ranges':invalid_absence_ranges,'invalid_task_types':invalid_task_types,'invalid_task_statuses':invalid_task_statuses,'invalid_confirmation_statuses':invalid_confirmation_statuses,'reschedule_without_suggested_time':reschedule_without_suggested_time,'rejected_without_comment':rejected_without_comment,'reschedule_requested_without_comment':reschedule_requested_without_comment,'warnings':warnings,'datasets':(source_info or {}).get('datasets',{})}
