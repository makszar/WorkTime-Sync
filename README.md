# WorkTime Sync

WorkTime Sync — MVP веб-системы для актуализации рабочего времени сотрудников.

## Что делает проект

MVP умеет:

- показывать дашборд состояния команды;
- показывать список сотрудников и их статусы;
- открывать карточку сотрудника;
- находить встречи вне рабочего времени;
- выявлять расхождения между HR-профилем и рабочим графиком;
- учитывать отпуск, командировку и личные часы;
- рассчитывать актуальность графика, загрузку и риск;
- показывать командную доступность;
- подбирать лучшие окна для встречи;
- формировать рекомендации и уведомления;
- объяснять риск по сотруднику;
- группировать сотрудников по состояниям;
- принимать загрузку JSON/CSV-данных через backend.

## Структура

```text
frontend/ — React + Vite интерфейс
backend/  — FastAPI backend с аналитикой, API, тестами и загрузкой данных
data/     — данные проекта
docs/     — документация
```

## Источник данных

Главный источник данных для backend:

```text
data/synthetic/
```

Используются:

```text
data/synthetic/employees.csv
data/synthetic/events.csv
data/synthetic/hr_profiles.csv
data/synthetic/absences.csv
data/synthetic/users.json
```

`backend/data/` оставлен только как временный fallback. Для командной работы обновляйте именно `data/synthetic`.

## Backend

Текущая версия backend: **1.4.0**.

Backend:

- читает данные из `data/synthetic`;
- валидирует данные через Pydantic;
- нормализует `emp001`, `evt001`, `abs001`;
- поддерживает `Mon|Tue|Wed|Thu|Fri` в CSV;
- поддерживает demo-login;
- поддерживает фильтр `department`;
- проверяет качество данных;
- поддерживает безопасную загрузку файлов;
- содержит backend-тесты.

## API

```http
POST /auth/login
GET /health
GET /health/data
GET /data/source
GET /schemas
GET /api/worktime/overview
GET /employees
GET /employees/{employee_id}
GET /employees/{employee_id}/risk-explanation
GET /analytics/summary
GET /analytics/conflicts
GET /analytics/data-mismatches
GET /analytics/data-quality
GET /analytics/availability
GET /analytics/groups
GET /recommendations
GET /notifications
GET /meeting-slots
POST /upload/{dataset}
```

Многие endpoint'ы поддерживают фильтр:

```text
?department=Product
?department=QA
?department=HR
?department=Sales
?department=Support
?department=Operations
```

## Demo-login

```text
product_manager / test1
qa_manager / test2
hr_manager / test3
sales_manager / test4
support_manager / test5
ops_manager / test6
```

## Frontend с backend

В `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_USE_MOCK_DATA=false
```

## Запуск backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Тесты backend

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

## GitHub Actions

Добавлен workflow:

```text
.github/workflows/backend-ci.yml
```

Он запускает backend-тесты при push и pull request в `main`.

Deploy workflow может падать из-за SSH-ключей — это отдельная проблема деплоя, не backend-кода.
