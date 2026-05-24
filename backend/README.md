# WorkTime Sync Backend

Backend версия: **2.5.0**.

Доработки по пункту 9 из `docs/missing_information_UPDATED.md`:

- `POST /tasks/{task_id}/apply` — финальное применение решения руководителем/HR/executive.
- `save_events(events)` — сохранение изменённых встреч обратно в active data source.
- `history` в задачах — журнал действий по задаче.
- `POST /tasks/generate-from-conflicts` — автогенерация задач по встречам вне рабочего времени.
- Расширенная `data-quality` диагностика workflow-ошибок.
- Backend-тесты для apply/generate/history/data-quality.

## Быстрая проверка

```http
POST /tasks/11/apply?user_id=u1
POST /tasks/generate-from-conflicts?user_id=u1
GET /analytics/data-quality
GET /tasks?user_id=u1
```

## Тесты

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```
