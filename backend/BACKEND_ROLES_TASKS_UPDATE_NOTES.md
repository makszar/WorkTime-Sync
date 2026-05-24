# Backend roles/tasks update

Архив реализует следующий этап из `docs/missing_information_UPDATED.md`:

- machine roles and scopes;
- role/scope filtering;
- tasks dataset;
- task API;
- schedule confirmation;
- department risk weights;
- extended risk explanation;
- executive analytics;
- HR dashboard;
- employee cabinet backend endpoint;
- tests for roles and tasks.

После замены файлов:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Проверить:

```text
GET /api/worktime/overview?user_id=u0
GET /api/worktime/overview?user_id=u1
GET /api/worktime/overview?user_id=emp5
GET /tasks?user_id=u1
GET /tasks/my?user_id=emp5
GET /analytics/company?user_id=u0
GET /analytics/hr-dashboard?user_id=u_hr
GET /employees/5/risk-explanation?user_id=u1
```
