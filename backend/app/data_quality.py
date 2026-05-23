from __future__ import annotations
from collections import Counter
from datetime import date, datetime
from typing import Any, Dict, List

def _duplicates(values:list[int])->list[int]:
    c=Counter(values); return sorted([v for v,n in c.items() if n>1])
def build_data_quality(employees:List[Dict[str,Any]],events:List[Dict[str,Any]],hr_profiles:List[Dict[str,Any]],absences:List[Dict[str,Any]],source_info:Dict[str,Any]|None=None,tasks:List[Dict[str,Any]]|None=None,schedule_confirmations:List[Dict[str,Any]]|None=None)->Dict[str,Any]:
    tasks=tasks or []; schedule_confirmations=schedule_confirmations or []
    employee_ids={int(e['id']) for e in employees}; event_ids=[int(e['id']) for e in events]; absence_ids=[int(a['id']) for a in absences]; task_ids=[int(t['id']) for t in tasks]; hr_ids={int(p['employee_id']) for p in hr_profiles}
    orphan_events=[{'event_id':int(e['id']),'employee_id':int(e['employee_id']),'title':e.get('title','')} for e in events if int(e['employee_id']) not in employee_ids]
    orphan_absences=[{'absence_id':int(a['id']),'employee_id':int(a['employee_id']),'type':a.get('type','')} for a in absences if int(a['employee_id']) not in employee_ids]
    orphan_tasks=[{'task_id':int(t['id']),'employee_id':int(t['employee_id']),'title':t.get('title','')} for t in tasks if int(t['employee_id']) not in employee_ids]
    orphan_confirmations=[{'employee_id':int(c['employee_id']),'status':c.get('status','')} for c in schedule_confirmations if int(c['employee_id']) not in employee_ids]
    orphan_hr_profiles=[{'employee_id':int(p['employee_id'])} for p in hr_profiles if int(p['employee_id']) not in employee_ids]
    employees_without_hr_profile=[{'employee_id':int(e['id']),'name':e.get('name',''),'team':e.get('team','')} for e in employees if int(e['id']) not in hr_ids]
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
    blocking=orphan_events or orphan_absences or invalid_event_ranges or invalid_absence_ranges or _duplicates([int(e['id']) for e in employees]) or _duplicates(event_ids) or _duplicates(absence_ids) or _duplicates(task_ids)
    return {'status':'warning' if warnings and not blocking else ('error' if blocking else 'ok'),'source':(source_info or {}).get('active_source'),'employees':len(employees),'events':len(events),'hr_profiles':len(hr_profiles),'absences':len(absences),'tasks':len(tasks),'schedule_confirmations':len(schedule_confirmations),'teams':sorted({e.get('team','') for e in employees if e.get('team')}),'duplicate_employee_ids':_duplicates([int(e['id']) for e in employees]),'duplicate_event_ids':_duplicates(event_ids),'duplicate_absence_ids':_duplicates(absence_ids),'duplicate_task_ids':_duplicates(task_ids),'orphan_events':orphan_events,'orphan_absences':orphan_absences,'orphan_tasks':orphan_tasks,'orphan_confirmations':orphan_confirmations,'orphan_hr_profiles':orphan_hr_profiles,'employees_without_hr_profile':employees_without_hr_profile,'invalid_event_ranges':invalid_event_ranges,'invalid_absence_ranges':invalid_absence_ranges,'warnings':warnings,'datasets':(source_info or {}).get('datasets',{})}
