# WorkTime Sync Backend

Backend версия: **2.3.0**.

Добавлены задачи по встречам, расширенная проверка tasks, enriched task responses и workflow для `EmployeeCabinet`, `HRDashboard` и `ExecutiveDashboard`.

## Новые типы задач

```text
confirm_schedule
review_hr_profile
review_load
update_timezone
meeting_confirmation
reschedule_meeting
meeting_outside_work_approval
```

## Новые поля задач

```json
{
  "related_event_id": 2,
  "meeting_action": "approve_outside_work",
  "suggested_start_datetime": "2026-05-20T16:00:00",
  "suggested_end_datetime": "2026-05-20T16:45:00"
}
```

Backend проверяет, что событие существует, относится к тому же сотруднику, а для `meeting_outside_work_approval` действительно выходит за рабочий график.

## Endpoint'ы

```http
GET /tasks?user_id=u1
GET /tasks/my?user_id=emp5
POST /tasks?user_id=u1
PATCH /tasks/{task_id}/status?user_id=emp5
GET /employees/me?user_id=emp5
GET /analytics/company?user_id=u0
GET /analytics/hr-dashboard?user_id=u_hr
GET /analytics/data-quality
```

## Тесты

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```
