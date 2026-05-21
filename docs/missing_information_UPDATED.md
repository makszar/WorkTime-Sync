# Что отсутствует или требует уточнения по текущему состоянию WorkTime Sync

## Уже реализовано

### Frontend

- React + Vite интерфейс.
- Дашборд.
- Список сотрудников.
- Карточка сотрудника.
- Конфликты.
- Командная доступность.
- Рекомендации.
- Подключение к backend через `/api/worktime/overview`.
- Публичный сайт `https://worktimesync.ru/`.

### Backend

- FastAPI backend.
- `GET /health`.
- `GET /api/worktime/overview`.
- `GET /employees`.
- `GET /employees/frontend`.
- `GET /employees/{employee_id}`.
- `GET /employees/{employee_id}/risk-explanation`.
- `GET /analytics/summary`.
- `GET /analytics/conflicts`.
- `GET /analytics/data-mismatches`.
- `GET /analytics/availability`.
- `GET /analytics/groups`.
- `GET /recommendations`.
- `GET /notifications`.
- `GET /meeting-slots`.
- `POST /upload/{dataset}`.
- CSV/JSON data loader.
- Основной источник данных `data/synthetic`.
- Fallback на `backend/data`.
- Нормализация id вида `emp001`, `evt001`, `abs001`.
- Нормализация ISO datetime с timezone offsets.
- Pydantic-валидация.
- Расчёт актуальности, загрузки, конфликтов и риска.
- Группы сотрудников.
- Объяснение риска.
- Уведомления.
- Backend-тесты.
- GitHub Actions деплой через `deploy.yml`.

### Data

- `data/synthetic/employees.csv`.
- `data/synthetic/events.csv`.
- `data/synthetic/hr_profiles.csv`.
- `data/synthetic/absences.csv`.
- 10 сотрудников.
- 37 событий.
- 6 команд.
- Отсутствия vacation/sick_leave.

## Что требует уточнения или доработки

### 1. README в корне

Корневой README нужно держать синхронизированным с фактическим API.

Особенно важно указать:

- `data/synthetic` как основной источник данных;
- 10 сотрудников вместо старых 6;
- новые endpoint'ы:
  - `/employees/{employee_id}/risk-explanation`;
  - `/analytics/groups`;
  - `/notifications`;
- что `backend/data` теперь fallback.

### 2. Frontend не показывает все backend-возможности

Backend уже умеет:

- risk explanation;
- groups;
- notifications;
- data mismatches.

Но в текущем frontend явно показаны только:

- дашборд;
- сотрудники;
- карточка;
- конфликты;
- доступность;
- рекомендации.

Можно добавить frontend-экраны:

- “Группы”;
- “Уведомления”;
- “Расхождения HR”;
- “Почему такой риск”.

### 3. Настоящая база данных

Сейчас основной источник данных — CSV/JSON в `data/synthetic`.

Для production нужно заменить файловое хранилище на:

- PostgreSQL;
- SQLite;
- другую БД.

Но текущая архитектура уже подготовлена: data layer можно заменить без переписывания всей аналитики.

### 4. Реальные интеграции

Сейчас календарь, HR, task-tracker и отсутствия имитируются через CSV/JSON.

Нужно подключить:

- Google Calendar;
- HRM;
- Jira/YouTrack;
- табель;
- корпоративные уведомления.

### 5. Авторизация и роли

В кейсе есть роли:

- сотрудник;
- HR;
- руководитель;
- PM;
- администратор;
- аналитик.

Сейчас роли используются в логике рекомендаций/уведомлений, но полноценной авторизации и прав доступа пока нет.

### 6. UI для загрузки данных

Backend endpoint `POST /upload/{dataset}` есть.

Нужен frontend-экран, где пользователь может загрузить:

- employees.csv;
- events.csv;
- hr_profiles.csv;
- absences.csv.

### 7. Уведомления

Backend формирует уведомления, но пока это не реальные push/email/Telegram-уведомления.

Следующий шаг:

- отправка email;
- Telegram-бот;
- Slack/Teams;
- push в интерфейсе.

### 8. AI-ассистент

В кейсе можно развить AI-слой.

Сейчас есть объяснимые правила и risk explanation, но нет отдельного чат-ассистента.

### 9. История изменений

Пока нет истории изменений графиков.

Нужно хранить:

- кто изменил график;
- когда;
- что было до/после;
- причина изменения.

### 10. Тестовое покрытие

Backend-тесты есть, но можно расширить:

- загрузка CSV;
- загрузка JSON;
- невалидные файлы;
- groups;
- notifications;
- risk explanation;
- public deployment smoke-test.
