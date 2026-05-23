# WorkTime Sync Backend

Backend — аналитический и workflow-контур WorkTime Sync.

Текущая версия: **2.2.0**.

## Что добавлено

- роли `executive`, `department_manager`, `hr`, `employee`;
- scope-фильтрация `all`, `department`, `self`;
- `tasks.json` и task API;
- `schedule_confirmations.json` и подтверждение графика;
- риск с весами по отделам;
- расширенный `risk-explanation`;
- `/analytics/company` для полного руководителя;
- `/analytics/hr-dashboard` для HR;
- `/employees/me` для сотрудника.

## Основные данные

```text
data/synthetic/employees.csv
data/synthetic/events.csv
data/synthetic/hr_profiles.csv
data/synthetic/absences.csv
data/synthetic/users.json
data/synthetic/tasks.json
data/synthetic/schedule_confirmations.json
```

## Роли

| Role | Scope | Что видит |
|---|---|---|
| `executive` | `all` | всю компанию |
| `hr` | `all` | всех сотрудников с HR-фокусом |
| `department_manager` | `department` | только свой отдел |
| `employee` | `self` | только себя |

## Новые endpoint'ы

```http
GET /tasks
GET /tasks/my
POST /tasks
GET /tasks/{task_id}
PATCH /tasks/{task_id}/status
PATCH /employees/{employee_id}/confirm-schedule
GET /employees/me
GET /analytics/company
GET /analytics/hr-dashboard
```

## Scope-примеры

```text
GET /api/worktime/overview?user_id=u0      # executive, вся компания
GET /api/worktime/overview?user_id=u1      # Core Platform manager
GET /api/worktime/overview?user_id=emp5    # один сотрудник
```

Старый department-фильтр сохранён:

```text
GET /api/worktime/overview?department=Core%20Platform
```

## Риск с весами отделов

```text
R = wA * (1 - A)
  + wC * C
  + wL * L
  + wT * timezone_mismatch
  + wH * hr_mismatch
```

| Отдел | wA | wC | wL | wT | wH |
|---|---:|---:|---:|---:|---:|
| Core Platform | 0.25 | 0.25 | 0.30 | 0.10 | 0.10 |
| Product UI | 0.25 | 0.30 | 0.25 | 0.10 | 0.10 |
| People Ops | 0.30 | 0.15 | 0.20 | 0.10 | 0.25 |
| Delivery | 0.20 | 0.30 | 0.30 | 0.10 | 0.10 |
| Quality | 0.20 | 0.25 | 0.35 | 0.10 | 0.10 |

## Запуск

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8040 --reload
```

## Тесты

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```
