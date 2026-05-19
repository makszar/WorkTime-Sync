# WorkTime Sync Backend MVP

Минимальный backend-проект для хакатонного MVP WorkTime Sync.

## Что уже есть

- Чтение тестовых данных из JSON.
- Подготовлена функция `load_table()`, которая умеет читать JSON или CSV.
- API `GET /employees` — список сотрудников с краткими метриками.
- API `GET /employees/{id}` — карточка сотрудника, события, HR-профиль, рекомендации.
- API `GET /analytics/summary` — общая аналитика по команде.
- Расчёты:
  - `days_since_update`
  - `schedule_actuality`
  - `outside_work_ratio`
  - `load`
  - `risk`
  - `risk_status`

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

После запуска открой:

```text
http://127.0.0.1:8000/docs
```

## Основные endpoint'ы

```text
GET /employees
GET /employees/1
GET /analytics/summary
```

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

## Следующий шаг

Добавить endpoint'ы:

```text
GET /analytics/conflicts
GET /analytics/availability
GET /recommendations
GET /meeting-slots
POST /upload
```
