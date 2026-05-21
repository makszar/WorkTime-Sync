# WorkTime Sync Backend

Backend адаптирован под React/Vite frontend и расширен как аналитический контур для хакатонного MVP.

## Главный endpoint для frontend

Frontend при `VITE_USE_MOCK_DATA=false` делает один запрос:

```text
GET /api/worktime/overview
```

Ответ содержит всё, что нужно текущему frontend:

```json
{
  "employees": [],
  "events": [],
  "roadmap": [],
  "summary": {},
  "recommendations": [],
  "bestSlots": [],
  "notifications": [],
  "groups": {}
}
```

Поля `notifications` и `groups` добавлены поверх текущего frontend-контракта. Они не ломают старый UI, но позволяют показать более сильную backend-аналитику в Swagger.

## Endpoint'ы

```text
GET /
GET /health
GET /api/worktime/overview
GET /employees
GET /employees/frontend
GET /employees/{employee_id}
GET /employees/{employee_id}/risk-explanation
GET /analytics/summary
GET /analytics/conflicts
GET /analytics/data-mismatches
GET /analytics/availability
GET /analytics/groups
GET /recommendations
GET /notifications
GET /meeting-slots
POST /upload/{dataset}
```

## Что улучшено в версии 1.2.0

- Добавлен `GET /analytics/groups` — группы сотрудников: актуальные, устаревшие, с внешними встречами, высокой загрузкой, конфликтом часового пояса, HR-расхождением, требующие подтверждения.
- Добавлен `GET /employees/{employee_id}/risk-explanation` — объяснение риска по факторам и формуле.
- Добавлен `GET /notifications` — уведомления для HR, руководителя и PM на основе риска, перегрузки, конфликтов и расхождений.
- Улучшены demo-данные в `events.json`, чтобы перегрузка сотрудника реально считалась backend-формулой.
- Добавлены `response_model` для ключевых endpoint'ов Swagger.
- CSV/upload доработан: если загружен CSV, он реально используется вместо JSON; невалидные файлы отклоняются через Pydantic-валидацию.
- Availability и meeting-slots учитывают рабочие часы, календарные события, focus-блоки, absence и перегруз.
- Добавлены автоматические backend-тесты.

## Данные

Основная папка данных для backend:

```text
data/synthetic/
```

Backend ожидает в этой папке backend-ready файлы:

```text
data/synthetic/employees.json
data/synthetic/events.json
data/synthetic/hr_profiles.json
data/synthetic/absences.json
```

Также поддерживаются CSV-файлы с такими же dataset-name:

```text
data/synthetic/employees.csv
data/synthetic/events.csv
data/synthetic/hr_profiles.csv
data/synthetic/absences.csv
```

Если в `data/synthetic` есть CSV и JSON для одного dataset, CSV имеет приоритет:

```text
employees.csv -> читается вместо employees.json
events.csv -> читается вместо events.json
hr_profiles.csv -> читается вместо hr_profiles.json
absences.csv -> читается вместо absences.json
```

`backend/data/` оставлен только как временный fallback. Это значит, что если нужного файла нет в `data/synthetic`, backend попробует найти его в `backend/data`.

Главный источник данных команды — `data/synthetic`. Для демо и командной работы обновлять нужно именно эту папку, а не `backend/data`.

Можно переопределить источник данных локально через переменную окружения:

```powershell
$env:WORKTIME_DATA_DIR="C:\path\to\WorkTime-Sync\data\synthetic"
```

## Расчёты

Backend считает обязательные для MVP показатели:

```text
days_since_update = DEMO_TODAY - last_update_date
schedule_actuality = max(0, 1 - days_since_update / 90)
outside_work_ratio = outside_work_events / total_events
load = busy_hours / work_hours
risk = 0.30 * (1 - schedule_actuality)
     + 0.25 * outside_work_ratio
     + 0.25 * load
     + 0.10 * timezone_mismatch
     + 0.10 * hr_mismatch
```

Дополнительно разделены:

```text
calendar_conflict_count — встречи/события вне рабочего графика
data_mismatch_count — расхождения HR/часового пояса
issue_count — общий счётчик проблем
```

`DEMO_TODAY = 2026-05-19` зафиксирован для воспроизводимого демо. В production это можно заменить на `date.today()` или на выбранный период анализа.

## Запуск backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

API-документация:

```text
http://127.0.0.1:8000/docs
```

## Тесты

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

Ожидаемый результат:

```text
passed
```

## Запуск frontend с backend

В папке `frontend` создать `.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_USE_MOCK_DATA=false
```

Потом:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Открыть сайт:

```text
http://localhost:5173
```

## Что остаётся future work

- База данных: SQLite/PostgreSQL вместо файлов.
- Авторизация и роли.
- Реальные интеграции с Google Calendar, HRM, task-tracker и табелем.
- Отдельный AI-chat-ассистент поверх рассчитанных метрик.
- История изменений графиков.
