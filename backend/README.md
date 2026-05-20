# WorkTime Sync Backend

Backend адаптирован под текущий React/Vite frontend и закрывает ключевые MVP-требования по аналитике рабочего времени.

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
  "bestSlots": [],
  "availability": [],
  "dataMismatches": []
}
```

## Endpoint'ы

```text
GET /
GET /health
GET /api/worktime/overview
GET /employees
GET /employees/frontend
GET /employees/{employee_id}
GET /analytics/summary
GET /analytics/conflicts
GET /analytics/data-mismatches
GET /analytics/availability
GET /recommendations
GET /meeting-slots
POST /upload/{dataset}
```

## Что доработано

- CSV/JSON загрузка теперь реально влияет на данные API: если загружен `employees.csv`, backend читает его вместо `employees.json`.
- При загрузке нового CSV/JSON старый файл другого формата для этого dataset удаляется, чтобы не было stale-данных.
- Данные проходят Pydantic-валидацию при чтении.
- Командная доступность учитывает:
  - рабочие дни;
  - рабочие часы;
  - календарные события;
  - отпуска, личные часы и командировки;
  - перегруз.
- Лучшие слоты строятся на основе той же доступности.
- Разделены:
  - `calendar_conflict_count` — встречи вне рабочего времени;
  - `data_mismatch_count` — расхождения с HR/часовым поясом;
  - `issue_count` — суммарные проблемы.
- Добавлены backend-тесты.

## Формулы

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

`DEMO_TODAY = 2026-05-19` и `DEMO_WEEK_START = 2026-05-18` зафиксированы специально, чтобы демо было воспроизводимым и метрики не менялись каждый день.

## Данные

Данные лежат в `backend/data`:

```text
employees.json
hr_profiles.json
events.json
absences.json
```

CSV формат тоже поддерживается. Для массива `work_days` в CSV используй `;`:

```csv
id,name,team,role,timezone,work_start,work_end,work_days,work_format,last_update_date
1,Анна,People,HR,Europe/Moscow,09:00,18:00,Mon;Tue;Wed;Thu;Fri,hybrid,2026-05-01
```

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

## Тесты

```bash
cd backend
pytest
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
