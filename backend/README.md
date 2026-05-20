# WorkTime Sync Backend

Backend полностью адаптирован под текущий React/Vite frontend.

## Главный endpoint для frontend

Frontend при `VITE_USE_MOCK_DATA=false` делает один запрос:

```text
GET /api/worktime/overview
```

Ответ соответствует форме, которую ждёт `src/App.jsx`:

```json
{
  "employees": [],
  "events": [],
  "roadmap": [],
  "summary": {},
  "recommendations": [],
  "bestSlots": []
}
```

## Остальные endpoint'ы

```text
GET /
GET /health
GET /employees
GET /employees/frontend
GET /employees/{employee_id}
GET /analytics/summary
GET /analytics/conflicts
GET /analytics/availability
GET /recommendations
GET /meeting-slots
POST /upload/{dataset}
```

## Расчёты

Backend считает обязательные для MVP показатели:

```text
days_since_update = today - last_update_date
schedule_actuality = max(0, 1 - days_since_update / 90)
outside_work_ratio = outside_work_events / total_events
load = busy_hours / work_hours
risk = 0.30 * (1 - schedule_actuality)
     + 0.25 * outside_work_ratio
     + 0.25 * load
     + 0.10 * timezone_mismatch
     + 0.10 * hr_mismatch
```

Также считаются:

```text
conflicts
availability map
best meeting slots
recommendations
roadmap
risk status
```

## Данные

Данные лежат в `backend/data`:

```text
employees.json
hr_profiles.json
events.json
absences.json
```

Поддержка CSV оставлена в `data_loader.py`.

## Запуск backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows PowerShell/CMD
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API-документация:

```text
http://127.0.0.1:8000/docs
```

## Запуск frontend с backend

В папке `frontend` создай `.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_USE_MOCK_DATA=false
```

Потом:

```bash
cd frontend
npm.cmd install
npm.cmd run dev
```

Открыть сайт:

```text
http://localhost:5173
```
