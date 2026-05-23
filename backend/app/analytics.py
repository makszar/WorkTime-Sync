from __future__ import annotations
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional
MAX_DAYS_WITHOUT_UPDATE=90
DEMO_TODAY=date(2026,5,19)
WEEKDAY_BY_INDEX={0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri',5:'Sat',6:'Sun'}
RU_WEEKDAY={'Mon':'Пн','Tue':'Вт','Wed':'Ср','Thu':'Чт','Fri':'Пт','Sat':'Сб','Sun':'Вс'}
CODE_BY_RU={v:k for k,v in RU_WEEKDAY.items()}
FORMAT_LABEL={'remote':'Удаленно','hybrid':'Гибрид','office':'Офис'}
TIMEZONE_LABEL={'Europe/Moscow':'UTC+3','Asia/Yekaterinburg':'UTC+5','Asia/Samarkand':'UTC+5','Asia/Dubai':'UTC+4'}
PRIORITY_ORDER={'Срочно':0,'Важно':1,'В работе':2,'Планово':3}
DEFAULT_RISK_WEIGHTS={'actuality':0.30,'conflicts':0.25,'load':0.25,'timezone':0.10,'hr':0.10}
DEPARTMENT_RISK_WEIGHTS={
 'Core Platform':{'actuality':0.25,'conflicts':0.25,'load':0.30,'timezone':0.10,'hr':0.10},
 'Product UI':{'actuality':0.25,'conflicts':0.30,'load':0.25,'timezone':0.10,'hr':0.10},
 'People Ops':{'actuality':0.30,'conflicts':0.15,'load':0.20,'timezone':0.10,'hr':0.25},
 'Delivery':{'actuality':0.20,'conflicts':0.30,'load':0.30,'timezone':0.10,'hr':0.10},
 'Quality':{'actuality':0.20,'conflicts':0.25,'load':0.35,'timezone':0.10,'hr':0.10}}
DEPARTMENT_RISK_LOGIC={
 'Core Platform':'Для Core Platform повышен вес загрузки: перегруз инженеров влияет на стабильность разработки и интеграций.',
 'Product UI':'Для Product UI повышен вес встреч вне графика: дизайн-ревью и согласования требуют синхронизации.',
 'People Ops':'Для People Ops повышен вес актуальности и HR-расхождений: отдел отвечает за корректность кадровых данных.',
 'Delivery':'Для Delivery повышены веса конфликтов и нагрузки: планирование релизов зависит от доступности менеджеров.',
 'Quality':'Для Quality повышен вес нагрузки: перегруз QA влияет на качество релизов.'}
def parse_date(v): return date.fromisoformat(v)
def parse_datetime(v): return datetime.fromisoformat(v)
def parse_time(v): return time.fromisoformat(v)
def clamp(v,minimum=0,maximum=1): return min(max(v,minimum),maximum)
def round2(v): return round(v,2)
def percent(v): return round(clamp(v)*100)
def weekday_code(dt): return WEEKDAY_BY_INDEX[dt.weekday()]
def weekday_label(dt): return RU_WEEKDAY[weekday_code(dt)]
def risk_status(r): return 'низкий' if r<0.25 else ('средний' if r<0.50 else ('высокий' if r<0.75 else 'критический'))
def risk_tone(r): return 'critical' if r>=0.75 else ('high' if r>=0.50 else ('medium' if r>=0.25 else 'low'))
def risk_weights_for_department(dep): return DEPARTMENT_RISK_WEIGHTS.get(dep or '',DEFAULT_RISK_WEIGHTS)
def risk_formula_for_weights(w): return f"{w['actuality']:.2f}*(1-A)+{w['conflicts']:.2f}*C+{w['load']:.2f}*L+{w['timezone']:.2f}*T+{w['hr']:.2f}*H"
def department_logic(dep): return DEPARTMENT_RISK_LOGIC.get(dep or '','Для неизвестного отдела используются стандартные веса риска MVP.')
def employee_events(e,events): return [x for x in events if int(x['employee_id'])==int(e['id'])]
def employee_absences(e,absences): return [x for x in absences if int(x['employee_id'])==int(e['id'])]
def event_duration_hours(ev): return max(0,(parse_datetime(ev['end_datetime'])-parse_datetime(ev['start_datetime'])).total_seconds()/3600)
def daily_work_hours(e): return max(0,(datetime.combine(DEMO_TODAY,parse_time(e['work_end']))-datetime.combine(DEMO_TODAY,parse_time(e['work_start']))).total_seconds()/3600)
def weekly_work_hours(e): return daily_work_hours(e)*len(e.get('work_days',[]))
def is_event_outside_work_time(ev,e):
    st=parse_datetime(ev['start_datetime']); en=parse_datetime(ev['end_datetime'])
    return weekday_code(st) not in e['work_days'] or st.time()<parse_time(e['work_start']) or en.time()>parse_time(e['work_end'])
def hr_flags(e,hr):
    if not hr: return {'timezone_mismatch':0,'hr_mismatch':0}
    return {'timezone_mismatch':int(e['timezone']!=hr['hr_timezone']),'hr_mismatch':int(e['work_format']!=hr['hr_work_format'] or e['work_start']!=hr['hr_work_start'] or e['work_end']!=hr['hr_work_end'])}
def calculate_employee_metrics(employee,events,hr_profile,absences=None,today=DEMO_TODAY):
    absences=absences or []; evs=employee_events(employee,events); ab=employee_absences(employee,absences)
    days=max(0,(today-parse_date(employee['last_update_date'])).days); actuality=clamp(1-days/MAX_DAYS_WITHOUT_UPDATE)
    outside=sum(1 for ev in evs if is_event_outside_work_time(ev,employee)); total=len(evs); outside_ratio=outside/total if total else 0
    busy=sum(event_duration_hours(ev) for ev in evs); work=weekly_work_hours(employee); load=busy/work if work else 0
    flags=hr_flags(employee,hr_profile); w=risk_weights_for_department(employee.get('team'))
    risk=clamp(w['actuality']*(1-actuality)+w['conflicts']*outside_ratio+w['load']*load+w['timezone']*flags['timezone_mismatch']+w['hr']*flags['hr_mismatch'])
    data_mismatch=flags['timezone_mismatch']+flags['hr_mismatch']; issues=outside+data_mismatch+len(ab)
    return {'days_since_update':days,'schedule_actuality':round2(actuality),'outside_work_events':outside,'total_events':total,'outside_work_ratio':round2(outside_ratio),'busy_hours':round2(busy),'work_hours':round2(work),'load':round2(load),'timezone_mismatch':flags['timezone_mismatch'],'hr_mismatch':flags['hr_mismatch'],'absence_count':len(ab),'calendar_conflict_count':outside,'data_mismatch_count':data_mismatch,'issue_count':issues,'conflict_count':outside,'risk':round2(risk),'risk_status':risk_status(risk),'risk_tone':risk_tone(risk),'risk_weights':w,'risk_formula':risk_formula_for_weights(w),'department_logic':department_logic(employee.get('team'))}
def build_recommendation_texts(e,m):
    out=[]
    if m['days_since_update']>60: out.append('Обновить рабочий график: данные не актуализировались больше 60 дней.')
    if m['outside_work_ratio']>=0.3: out.append('Проверить встречи вне рабочего времени и перенести регулярные события.')
    if m['load']>=0.8: out.append('Проверить загрузку: календарь близок к перегрузке.')
    if m['timezone_mismatch']: out.append('Сверить часовой пояс сотрудника с HR-профилем.')
    if m['hr_mismatch']: out.append('Согласовать рабочий формат и часы с HR-данными.')
    if m.get('absence_count',0): out.append('Учесть временные исключения: отпуск, больничный или командировку.')
    return out or ['Критичных проблем не найдено, график выглядит актуальным.']
def build_status_note(m):
    if m['risk']>=0.75: return 'Критический риск: график нужно подтвердить в первую очередь.'
    if m['days_since_update']>MAX_DAYS_WITHOUT_UPDATE: return 'Данные не обновлялись больше 90 дней, график может быть устаревшим.'
    if m['outside_work_events']>0: return 'Есть встречи вне рабочего времени, стоит проверить календарь.'
    if m['timezone_mismatch'] or m['hr_mismatch']: return 'Есть расхождение с HR-профилем, нужно сверить данные.'
    if m['load']>=0.8: return 'Высокая загрузка: новые встречи лучше не добавлять.'
    return 'График выглядит актуальным, критичных проблем не найдено.'
def format_label(x): return FORMAT_LABEL.get(x,x)
def timezone_label(x): return TIMEZONE_LABEL.get(x,x)
def work_days_label(days): return [RU_WEEKDAY.get(d,d) for d in days]
def hour_int(v): return parse_time(v).hour
def to_frontend_employee(e,m):
    return {'id':int(e['id']),'name':e['name'],'role':e['role'],'team':e['team'],'format':format_label(e['work_format']),'timezone':timezone_label(e['timezone']),'workDays':work_days_label(e['work_days']),'workStart':hour_int(e['work_start']),'workEnd':hour_int(e['work_end']),'updatedAt':e['last_update_date'],'meetingsTotal':m['total_events'],'meetingsOutside':m['outside_work_events'],'busyHours':m['busy_hours'],'workHours':m['work_hours'],'timezoneMismatch':m['timezone_mismatch'],'hrCalendarMismatch':m['hr_mismatch'],'exceptions':build_recommendation_texts(e,m),'statusNote':build_status_note(m),'metrics':m}
def build_employee_list(employees,events,hr_profiles,absences=None):
    by={int(x['employee_id']):x for x in hr_profiles}; return [{**e,'metrics':calculate_employee_metrics(e,events,by.get(int(e['id'])),absences or [])} for e in employees]
def build_frontend_employee_list(employees,events,hr_profiles,absences=None): return [to_frontend_employee(x,x['metrics']) for x in build_employee_list(employees,events,hr_profiles,absences)]
def build_employee_card(employee_id,employees,events,hr_profiles,absences=None):
    e=next((x for x in employees if int(x['id'])==int(employee_id)),None)
    if not e: return None
    hr=next((x for x in hr_profiles if int(x['employee_id'])==int(employee_id)),None); m=calculate_employee_metrics(e,events,hr,absences or [])
    return {'employee':e,'frontend_employee':to_frontend_employee(e,m),'hr_profile':hr,'events':employee_events(e,events),'absences':employee_absences(e,absences or []),'metrics':m,'recommendations':build_recommendation_texts(e,m)}
def event_time_label(ev): return f"{parse_datetime(ev['start_datetime']).strftime('%H:%M')}-{parse_datetime(ev['end_datetime']).strftime('%H:%M')}"
def conflict_reason(ev,e):
    st=parse_datetime(ev['start_datetime']); en=parse_datetime(ev['end_datetime'])
    if weekday_code(st) not in e['work_days']: return 'Событие назначено в нерабочий день сотрудника.'
    if st.time()<parse_time(e['work_start']): return 'Событие начинается раньше заявленного рабочего времени.'
    if en.time()>parse_time(e['work_end']): return 'Событие заканчивается позже заявленного рабочего времени.'
    return 'Встреча выходит за пределы рабочего времени.'
def build_conflicts(employees,events):
    by={int(e['id']):e for e in employees}; out=[]
    for ev in events:
        e=by.get(int(ev['employee_id']))
        if e and is_event_outside_work_time(ev,e):
            st=parse_datetime(ev['start_datetime']); out.append({'id':int(ev['id']),'employeeId':int(e['id']),'employee':e['name'],'title':ev['title'],'day':weekday_label(st),'time':event_time_label(ev),'reason':conflict_reason(ev,e),'severity':'Высокая','source':ev.get('source','calendar'),'type':ev.get('type','meeting')})
    return out
def build_data_mismatches(employees,hr_profiles):
    by={int(x['employee_id']):x for x in hr_profiles}; out=[]
    for e in employees:
        hr=by.get(int(e['id']))
        if not hr: continue
        if e['timezone']!=hr['hr_timezone']: out.append({'id':f"timezone-{e['id']}",'employeeId':int(e['id']),'employee':e['name'],'type':'timezone','title':'Расхождение часового пояса','reason':f"В профиле: {timezone_label(e['timezone'])}, в HR: {timezone_label(hr['hr_timezone'])}.",'severity':'Средняя'})
        if e['work_format']!=hr['hr_work_format'] or e['work_start']!=hr['hr_work_start'] or e['work_end']!=hr['hr_work_end']: out.append({'id':f"hr-{e['id']}",'employeeId':int(e['id']),'employee':e['name'],'type':'hr_profile','title':'Расхождение с HR-профилем','reason':'Рабочий формат или часы отличаются от HR-данных.','severity':'Высокая'})
    return out
def build_summary(employees,events,hr_profiles,absences=None):
    items=build_employee_list(employees,events,hr_profiles,absences); total=len(items)
    if not total: return {'total_employees':0,'avg_risk':0,'avg_schedule_actuality':0,'avg_load':0,'total_conflicts':0,'calendar_conflicts':0,'data_mismatches':0,'total_outside_work_events':0,'outdated_employees':0,'high_risk_employees':0,'risk_distribution':{},'teams':[]}
    mets=[x['metrics'] for x in items]; conf=build_conflicts(employees,events); mism=build_data_mismatches(employees,hr_profiles); dist={'низкий':0,'средний':0,'высокий':0,'критический':0}
    for m in mets: dist[m['risk_status']]+=1
    teams={}
    for x in items:
        t=x['team']; teams.setdefault(t,{'team':t,'employees':0,'avg_risk':0,'total_conflicts':0,'avg_load':0}); teams[t]['employees']+=1; teams[t]['avg_risk']+=x['metrics']['risk']; teams[t]['total_conflicts']+=x['metrics']['calendar_conflict_count']; teams[t]['avg_load']+=x['metrics']['load']
    for t in teams.values(): t['avg_risk']=round2(t['avg_risk']/t['employees']); t['avg_load']=round2(t['avg_load']/t['employees'])
    return {'total_employees':total,'avg_risk':round2(sum(m['risk'] for m in mets)/total),'avg_schedule_actuality':round2(sum(m['schedule_actuality'] for m in mets)/total),'avg_load':round2(sum(m['load'] for m in mets)/total),'total_conflicts':len(conf),'calendar_conflicts':len(conf),'data_mismatches':len(mism),'total_outside_work_events':sum(m['outside_work_events'] for m in mets),'outdated_employees':sum(1 for m in mets if m['days_since_update']>MAX_DAYS_WITHOUT_UPDATE),'high_risk_employees':sum(1 for m in mets if m['risk']>=0.5),'risk_distribution':dist,'teams':list(teams.values())}
def build_frontend_summary(femps,conflicts):
    total=len(femps)
    if not total: return {'total':0,'current':0,'outdated':0,'highRisk':0,'conflicts':0,'averageLoad':0}
    return {'total':total,'current':sum(1 for e in femps if e['metrics']['schedule_actuality']>=0.7 and e['metrics']['risk']<0.5),'outdated':sum(1 for e in femps if e['metrics']['days_since_update']>MAX_DAYS_WITHOUT_UPDATE),'highRisk':sum(1 for e in femps if e['metrics']['risk']>=0.5),'conflicts':len(conflicts),'averageLoad':round(sum(e['metrics']['load'] for e in femps)/total*100)}
def slot_date(day_label):
    target=CODE_BY_RU[day_label]; monday=DEMO_TODAY-timedelta(days=DEMO_TODAY.weekday())
    for off in range(7):
        c=monday+timedelta(days=off)
        if WEEKDAY_BY_INDEX[c.weekday()]==target: return c
    return monday
def overlaps(a,b,c,d): return a<d and c<b
def build_availability(employees,events=None,hr_profiles=None,absences=None):
    events=events or []; absences=absences or []; days=['Пн','Вт','Ср','Чт','Пт']; rows=[]
    for day in days:
        slots=[]
        for hour in range(8,21):
            miss=[]; details=[]
            for e in employees:
                reason=None
                if CODE_BY_RU[day] not in e['work_days']: reason='нерабочий день'
                elif hour<hour_int(e['work_start']) or hour>=hour_int(e['work_end']): reason='вне рабочего времени'
                else:
                    s=datetime.combine(slot_date(day),time(hour=hour)); en=s+timedelta(hours=1)
                    for ev in employee_events(e,events):
                        if overlaps(s,en,parse_datetime(ev['start_datetime']),parse_datetime(ev['end_datetime'])): reason=f"занят: {ev['title']}"; break
                    for ab in employee_absences(e,absences):
                        if parse_date(ab['start_date'])<=slot_date(day)<=parse_date(ab['end_date']): reason=ab['type']; break
                if reason: miss.append(e['name']); details.append({'employee':e['name'],'reason':reason})
            count=max(0,len(employees)-len(miss)); typ='all' if count==len(employees) and employees else ('majority' if count>=max(1,round(len(employees)*0.65)) else 'weak')
            slots.append({'hour':hour,'count':count,'type':typ,'missing':miss,'missingDetails':details})
        rows.append({'day':day,'slots':slots})
    return rows
def build_best_slots(employees,events=None,hr_profiles=None,absences=None,limit=3):
    all=[]
    for row in build_availability(employees,events,hr_profiles,absences):
        for s in row['slots']: all.append({'label':f"{row['day']}, {s['hour']}:00-{s['hour']+1}:00",'count':s['count'],'missing':s['missing'],'missingDetails':s['missingDetails'],'hour':s['hour']})
    return [{k:v for k,v in s.items() if k!='hour'} for s in sorted(all,key=lambda x:(-x['count'],len(x['missing']),x['hour']))[:limit]]
def recommendation_task_type(kind): return {'График':'confirm_schedule','Часовой пояс':'update_timezone','Нагрузка':'review_load','HR-данные':'review_hr_profile','Встреча':'reschedule_meeting'}.get(kind)
def build_recommendations(employees,events,hr_profiles,absences=None):
    by={int(x['employee_id']):x for x in hr_profiles}; out=[]
    def add(item,eid=None,role=None): item['suggestedTaskType']=recommendation_task_type(item['type']); item['targetEmployeeId']=eid; item['targetRole']=role or 'HR'; out.append(item)
    for e in employees:
        m=calculate_employee_metrics(e,events,by.get(int(e['id'])),absences or []); eid=int(e['id'])
        if m['risk']>=0.5 or m['days_since_update']>60: add({'type':'График','title':f"Попросить {e['name']} подтвердить рабочий график",'reason':f"Риск {percent(m['risk'])}%, обновление было {m['days_since_update']} дней назад.",'priority':'Срочно' if m['risk']>=0.75 else 'Важно'},eid,'HR')
        if m['load']>=0.8: add({'type':'Нагрузка','title':f"Не назначать новые встречи: {e['name']}",'reason':f"Загрузка {percent(m['load'])}%.",'priority':'Срочно'},eid,'Руководитель')
        if m['timezone_mismatch']: add({'type':'Часовой пояс','title':f"Проверить часовой пояс: {e['name']}",'reason':'Часовой пояс сотрудника отличается от HR-профиля.','priority':'Важно'},eid,'HR')
        if m['hr_mismatch']: add({'type':'HR-данные','title':f"Сверить HR-профиль: {e['name']}",'reason':'Рабочий формат или часы отличаются от HR-данных.','priority':'Важно'},eid,'HR')
    for c in build_conflicts(employees,events)[:3]: add({'type':'Встреча','title':f"Перенести: {c['title']}",'reason':f"{c['employee']}, {c['day']} {c['time']}. {c['reason']}",'priority':'Срочно'},c['employeeId'],'PM')
    return sorted(out,key=lambda x:PRIORITY_ORDER.get(x['priority'],9))
def build_roadmap(summary): return [{'step':'1','title':'Подтвердить графики с высоким риском','owner':'HR','deadline':'Сегодня','state':'Срочно' if summary['highRisk'] else 'Планово'},{'step':'2','title':'Проверить часовые пояса и HR-расхождения','owner':'Руководитель','deadline':'До конца дня','state':'Важно'},{'step':'3','title':'Перенести регулярные встречи вне рабочего времени','owner':'PM','deadline':'Завтра','state':'В работе' if summary['conflicts'] else 'Готово'}]
def build_groups(employees,events,hr_profiles,absences=None):
    f=build_frontend_employee_list(employees,events,hr_profiles,absences); return {'actual':[e for e in f if e['metrics']['schedule_actuality']>=0.7 and e['metrics']['risk']<0.5],'outdated':[e for e in f if e['metrics']['days_since_update']>MAX_DAYS_WITHOUT_UPDATE],'outsideWorkMeetings':[e for e in f if e['metrics']['calendar_conflict_count']>0],'highLoad':[e for e in f if e['metrics']['load']>=0.8],'timezoneConflict':[e for e in f if e['metrics']['timezone_mismatch']],'hrMismatch':[e for e in f if e['metrics']['hr_mismatch']],'needsConfirmation':[e for e in f if e['metrics']['risk']>=0.5 or e['metrics']['days_since_update']>60]}
def impact(score): return 'high' if score>=0.6 else ('medium' if score>=0.25 else ('low' if score>0 else 'none'))
def confirmation_status_for_employee(eid,items=None):
    rec=[x for x in (items or []) if int(x['employee_id'])==int(eid)]
    return rec[-1].get('status','not_confirmed') if rec else 'not_confirmed'
def build_risk_explanation(employee_id,employees,events,hr_profiles,absences=None,schedule_confirmations=None):
    e=next((x for x in employees if int(x['id'])==int(employee_id)),None)
    if not e: return None
    hr=next((x for x in hr_profiles if int(x['employee_id'])==int(employee_id)),None); m=calculate_employee_metrics(e,events,hr,absences or []); w=m['risk_weights']; days=clamp(m['days_since_update']/MAX_DAYS_WITHOUT_UPDATE)
    raw=[('days_since_update','Давность обновления',days,m['days_since_update'],f"График обновлялся {m['days_since_update']} дней назад.",w['actuality']),('outside_work_ratio','Встречи вне рабочего времени',m['outside_work_ratio'],m['outside_work_ratio'],f"{m['outside_work_events']} из {m['total_events']} событий выходят за рабочий график.",w['conflicts']),('load','Загрузка',m['load'],m['load'],f"Занято {m['busy_hours']} ч из {m['work_hours']} рабочих часов за неделю.",w['load']),('timezone_mismatch','Часовой пояс',float(m['timezone_mismatch']),m['timezone_mismatch'],'Часовой пояс отличается от HR-профиля.' if m['timezone_mismatch'] else 'Расхождения часового пояса нет.',w['timezone']),('hr_mismatch','HR-данные',float(m['hr_mismatch']),m['hr_mismatch'],'Формат или часы отличаются от HR-профиля.' if m['hr_mismatch'] else 'Расхождения с HR-профилем нет.',w['hr'])]
    factors=[{'factor':f,'label':l,'value':v,'score':round2(s),'weightedScore':round2(s*wt),'weight':wt,'impact':impact(s),'explanation':ex} for f,l,s,v,ex,wt in raw]
    return {'employeeId':int(e['id']),'employee':e['name'],'department':e['team'],'risk':m['risk'],'riskStatus':m['risk_status'],'formula':'wA*(1-A)+wC*C+wL*L+wT*T+wH*H','weights':w,'departmentLogic':m['department_logic'],'formulaWithWeights':m['risk_formula'],'scheduleConfirmationStatus':confirmation_status_for_employee(employee_id,schedule_confirmations),'factors':factors,'recommendedActions':build_recommendation_texts(e,m)}
def build_notifications(employees,events,hr_profiles,absences=None):
    out=[]; by={int(x['employee_id']):x for x in hr_profiles}
    for e in employees:
        m=calculate_employee_metrics(e,events,by.get(int(e['id'])),absences or [])
        if m['risk']>=0.5 or m['days_since_update']>60: out.append({'id':f"confirm-{e['id']}",'recipientRole':'HR','employeeId':int(e['id']),'employee':e['name'],'title':'Запросить подтверждение рабочего графика','reason':f"Риск {percent(m['risk'])}%, последнее обновление {m['days_since_update']} дней назад.",'priority':'Срочно' if m['risk']>=0.75 else 'Важно','action':'send_schedule_confirmation_request','suggestedTaskType':'confirm_schedule'})
        if m['load']>=0.8: out.append({'id':f"load-{e['id']}",'recipientRole':'Руководитель','employeeId':int(e['id']),'employee':e['name'],'title':'Проверить перегруз сотрудника','reason':f"Загрузка {percent(m['load'])}%.",'priority':'Срочно','action':'review_employee_load','suggestedTaskType':'review_load'})
        if m['timezone_mismatch'] or m['hr_mismatch']: out.append({'id':f"data-{e['id']}",'recipientRole':'HR','employeeId':int(e['id']),'employee':e['name'],'title':'Сверить данные HR и календаря','reason':'Есть расхождение часового пояса, формата работы или рабочих часов.','priority':'Важно','action':'review_hr_profile','suggestedTaskType':'review_hr_profile'})
    for c in build_conflicts(employees,events)[:5]: out.append({'id':f"meeting-{c['id']}",'recipientRole':'PM','employeeId':c['employeeId'],'employee':c['employee'],'title':'Перенести встречу вне рабочего времени','reason':f"{c['title']}: {c['day']} {c['time']}. {c['reason']}",'priority':'Срочно','action':'reschedule_meeting','suggestedTaskType':'reschedule_meeting'})
    return sorted(out,key=lambda x:PRIORITY_ORDER.get(x['priority'],9))
def build_company_analytics(employees,events,hr_profiles,absences=None):
    s=build_summary(employees,events,hr_profiles,absences); items=sorted(build_employee_list(employees,events,hr_profiles,absences),key=lambda x:x['metrics']['risk'],reverse=True)[:5]
    return {'summary':s,'departments':s['teams'],'topRiskEmployees':[{'employeeId':int(x['id']),'employee':x['name'],'department':x['team'],'risk':x['metrics']['risk'],'riskStatus':x['metrics']['risk_status']} for x in items],'attentionDepartments':[t for t in s['teams'] if t['avg_risk']>=0.5 or t['total_conflicts']>0]}
def build_hr_dashboard(employees,events,hr_profiles,absences=None,tasks=None,schedule_confirmations=None):
    conf={int(x['employee_id']) for x in (schedule_confirmations or []) if x.get('status')=='confirmed'}
    return {'summary':build_summary(employees,events,hr_profiles,absences),'dataMismatches':build_data_mismatches(employees,hr_profiles),'timezoneConflicts':[m for m in build_data_mismatches(employees,hr_profiles) if m['type']=='timezone'],'outdatedEmployees':[{'employeeId':int(x['id']),'employee':x['name'],'department':x['team'],'daysSinceUpdate':x['metrics']['days_since_update']} for x in build_employee_list(employees,events,hr_profiles,absences) if x['metrics']['days_since_update']>MAX_DAYS_WITHOUT_UPDATE],'employeesWithoutConfirmation':[{'employeeId':int(e['id']),'employee':e['name'],'department':e['team']} for e in employees if int(e['id']) not in conf],'absences':absences or [],'hrTasks':[t for t in (tasks or []) if t.get('created_by_role')=='hr' or t.get('type') in {'review_hr_profile','confirm_schedule','update_timezone'}]}
def build_worktime_overview(employees,events,hr_profiles,absences=None):
    femps=build_frontend_employee_list(employees,events,hr_profiles,absences); conflicts=build_conflicts(employees,events); summary=build_frontend_summary(femps,conflicts)
    return {'employees':femps,'events':conflicts,'roadmap':build_roadmap(summary),'summary':summary,'recommendations':build_recommendations(employees,events,hr_profiles,absences),'bestSlots':build_best_slots(employees,events,hr_profiles,absences),'notifications':build_notifications(employees,events,hr_profiles,absences),'groups':build_groups(employees,events,hr_profiles,absences)}
