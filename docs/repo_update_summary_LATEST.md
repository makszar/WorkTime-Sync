# WorkTime Sync — repo update summary V2.9

## Проверенные файлы

- `README.md`
- `backend/app/main.py`
- `frontend/src/api/worktimeApi.js`
- `frontend/src/App.jsx`
- `frontend/src/components/TaskCard.jsx`
- `frontend/src/components/TaskForm.jsx`
- `frontend/src/pages/Availability.jsx`
- `frontend/src/components/AvailabilityGrid.jsx`

---

## Текущее состояние

Проект находится в состоянии **MVP V2.9**.

### Backend

Backend `2.9.0`.

Реализовано:

- FastAPI API;
- `/api` routes и старые routes без `/api`;
- demo-token auth;
- role/scope access;
- tasks API;
- meeting tasks;
- schedule confirmations;
- task history;
- `POST /api/tasks/{task_id}/apply`;
- `POST /api/tasks/generate-from-conflicts`;
- `save_events`;
- analytics endpoints;
- HR dashboard;
- company analytics;
- data-quality.

### Frontend

Frontend `v2.9`.

Реализовано:

- login screen;
- role-based routing;
- Executive dashboard;
- HR dashboard;
- Employee cabinet;
- Tasks page;
- Employees;
- Employee profile;
- Conflicts;
- Availability;
- Recommendations;
- API client through `/api/...`.

---

## Главные изменения относительно предыдущих версий

1. Backend поднят до V2.9.
2. Frontend использует `/api/...` paths.
3. Добавлены aliases backend routes с `/api`.
4. Исправлена основная причина потенциальных 405/404 при deploy.
5. Добавлена логика применения решения по задаче.
6. Добавлена автогенерация задач по конфликтам.
7. README обновлён под актуальное состояние.

---

## Текущие риски

1. UI кнопок задач ещё не полностью понятный.
2. Для `meeting_outside_work_approval` нет удобного сценария “Предложить другое время”.
3. В событиях может отображаться только день недели, а не дата.
4. Карта доступности показывает count и missing, но не полноценный список свободных сотрудников.
5. Нужно проверить deploy и nginx.
6. Нужно проверить права записи на сервере.
7. Нужны ручные end-to-end тесты.

---

## Рекомендация

До защиты не расширять продукт новыми большими модулями. Сфокусироваться на:

```text
UX задач → даты событий → доступность → deploy → demo сценарий
```
