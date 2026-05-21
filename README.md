# WorkTime Sync

WorkTime Sync — MVP веб-системы для актуализации рабочего времени сотрудников. Проект помогает компании видеть, насколько рабочие графики соответствуют реальной занятости, где есть встречи вне рабочего времени, кто перегружен, где расходятся HR-данные и календарь, какие сотрудники требуют подтверждения графика и какие действия нужно выполнить HR, руководителю или проектному менеджеру.

Проект сделан по кейсу №3 хакатона «Весенний код»: **актуализация рабочего времени сотрудников**.

## Что делает проект

WorkTime Sync решает проблему устаревших рабочих графиков и ручной сверки данных между календарём, HR-профилем, задачами, отсутствиями и фактической занятостью сотрудников.

MVP умеет:

- показывать дашборд состояния команды;
- показывать список сотрудников и их статусы;
- открывать карточку сотрудника;
- сравнивать заявленный график с календарными событиями;
- находить встречи и события вне рабочего времени;
- выявлять расхождения между HR-профилем и рабочим графиком;
- учитывать временные исключения: отпуск, больничный, командировку, личные часы;
- рассчитывать актуальность графика;
- рассчитывать загрузку сотрудника;
- рассчитывать интегральный риск неактуальности данных;
- объяснять риск по факторам;
- группировать сотрудников по проблемным категориям;
- показывать командную доступность;
- подбирать лучшие окна для встречи;
- формировать рекомендации для HR, руководителя и PM;
- формировать уведомления для ответственных ролей;
- принимать загрузку JSON/CSV-данных через backend.

Главная идея: **рабочий график должен стать живым источником планирования, а не устаревшей записью в HR-системе.**

## Текущее состояние проекта

В репозитории реализованы:

```text
frontend/         React + Vite интерфейс
backend/          FastAPI backend с аналитикой, API, загрузкой данных и тестами
data/synthetic/   основной источник синтетических данных MVP
docs/             вспомогательная документация
presentation/     материалы для презентации
tests/            ручные тест-кейсы
deploy.yml        GitHub Actions workflow для автодеплоя
```

## Frontend

Frontend реализован на React + Vite. В интерфейсе есть:

- дашборд;
- сотрудники;
- карточка сотрудника;
- конфликты;
- доступность;
- рекомендации.

Frontend работает в двух режимах:

1. **Mock-режим** — данные берутся из `frontend/src/data/mockData.js`.
2. **Backend-режим** — данные берутся из backend по endpoint:

```http
GET /api/worktime/overview
```

Для подключения frontend к backend в `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_USE_MOCK_DATA=false
```

## Backend

Backend реализован на FastAPI и адаптирован под React/Vite frontend.

Backend умеет:

- читать данные из `data/synthetic`;
- поддерживать CSV и JSON;
- валидировать данные через Pydantic;
- нормализовать строковые идентификаторы вида `emp001`, `evt001`, `abs001` в числовые id для аналитики;
- нормализовать datetime-значения с часовыми поясами;
- перечитывать данные при каждом запросе;
- считать метрики сотрудников;
- строить summary по команде;
- находить календарные конфликты;
- находить HR/data mismatches;
- строить карту командной доступности;
- подбирать лучшие слоты встречи;
- формировать рекомендации;
- формировать уведомления;
- объяснять риск сотрудника по факторам;
- группировать сотрудников по проблемным категориям;
- принимать загрузку JSON/CSV через API;
- запускать backend-тесты через `pytest`.

## Основной источник данных

После обновления v1.6 основной источник данных MVP — папка:

```text
data/synthetic/
```

Backend в первую очередь читает именно её. Ожидаемые dataset-файлы:

```text
data/synthetic/employees.csv
data/synthetic/events.csv
data/synthetic/hr_profiles.csv
data/synthetic/absences.csv
```

Также поддерживаются JSON-файлы с теми же именами. Если для одного dataset есть и CSV, и JSON, приоритет имеет CSV.

Папка `backend/data/` оставлена как временный fallback: если нужный файл не найден в `data/synthetic`, backend попробует найти его в `backend/data`.

## Какие данные используются сейчас

### employees.csv

Файл сотрудников, отделов и рабочих графиков. Текущие поля:

- `id`;
- `name`;
- `team`;
- `role`;
- `timezone`;
- `work_start`;
- `work_end`;
- `work_days`;
- `work_format`;
- `last_update_date`.

На текущем этапе в `data/synthetic/employees.csv` — **10 сотрудников**:

1. Анна Иванова — Product Lead, Product.
2. Дмитрий Соколов — Backend Developer, Product.
3. Елена Петрова — UX/UI Designer, Product.
4. Иван Ким — QA Engineer, QA.
5. Мария Смирнова — Business Analyst, Product.
6. Павел Орлов — HR Manager, HR.
7. Алина Волкова — Sales Manager, Sales.
8. Сергей Морозов — Support Specialist, Support.
9. Ольга Федорова — Operations Coordinator, Operations.
10. Тимур Ахметов — Project Manager, Product.

Отделы/команды подтягиваются из поля `team`, а не задаются вручную. В текущих данных есть команды:

```text
Product
QA
HR
Sales
Support
Operations
```

### events.csv

Файл календарных событий. Сейчас в `data/synthetic/events.csv` — **37 событий**. Они имитируют данные из календаря, Jira/task-tracker, HR-календаря и support-календаря.

Используется для:

- расчёта занятых часов;
- поиска встреч вне рабочего времени;
- расчёта загрузки;
- построения конфликтов;
- построения доступности;
- подбора лучших окон встречи.

### hr_profiles.csv

Файл HR-профилей. Содержит HR-версию данных по сотрудникам:

- `employee_id`;
- `hr_timezone`;
- `hr_work_format`;
- `hr_work_start`;
- `hr_work_end`.

Используется для поиска расхождений между фактическим/заявленным графиком и HR-системой.

### absences.csv

Файл отсутствий и исключений. Сейчас используются:

- `vacation`;
- `sick_leave`.

Эти данные учитываются при командной доступности и подборе слотов.

## Как подтягиваются сотрудники и отделы

Количество сотрудников и отделов считается автоматически на основе данных.

Backend:

1. читает `data/synthetic/employees.csv` или `employees.json`;
2. валидирует строки через Pydantic-модель `Employee`;
3. нормализует id вида `emp001` в числовой id;
4. считает сотрудников через длину списка;
5. берёт отделы из поля `team`;
6. группирует сотрудников по командам;
7. пересчитывает summary, риски, группы и рекомендации.

Если в `employees.csv` добавить нового сотрудника или новый отдел, backend использует эти данные при следующем запросе без изменения кода.

## Реализованные API

```http
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

### GET /api/worktime/overview

Главный endpoint для frontend. Возвращает общий объект для интерфейса:

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

### GET /employees/{employee_id}/risk-explanation

Возвращает объяснение риска сотрудника: итоговый риск, статус, формулу, факторы, вклад каждого фактора и рекомендуемые действия.

### GET /analytics/groups

Возвращает группы сотрудников:

- `actual`;
- `outdated`;
- `outsideWorkMeetings`;
- `highLoad`;
- `timezoneConflict`;
- `hrMismatch`;
- `needsConfirmation`.

### GET /notifications

Возвращает уведомления для ролей: HR, руководитель, PM.

### POST /upload/{dataset}

Позволяет загрузить CSV/JSON для dataset:

```text
employees
events
hr_profiles
absences
```

Загрузка сохраняется в `data/synthetic`, чтобы это было единым источником данных команды.

## Основные формулы

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

Также отдельно считаются:

```text
calendar_conflict_count
data_mismatch_count
issue_count
absence_count
risk_status
risk_tone
```

`DEMO_TODAY = 2026-05-19` зафиксирован, чтобы демо было воспроизводимым и метрики не менялись каждый день.

## Архитектура

```text
Пользователь
   ↓
Frontend React + Vite
   ↓
frontend/src/api/worktimeApi.js
   ↓
GET /api/worktime/overview
   ↓
Backend FastAPI
   ↓
data_loader.py
   ↓
data/synthetic/*.csv или *.json
   ↓
analytics.py
   ↓
Метрики, риски, конфликты, группы, уведомления, рекомендации
```

## Как запустить backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Документация API:

```text
http://127.0.0.1:8000/docs
```

Проверка:

```text
http://127.0.0.1:8000/health
```

## Как запустить frontend

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Открыть сайт:

```text
http://localhost:5173
```

## Как запустить frontend с backend

В папке `frontend` создать `.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_USE_MOCK_DATA=false
```

После этого frontend берёт данные из:

```http
GET /api/worktime/overview
```

## Как запустить backend-тесты

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

## Деплой

В корне репозитория есть `deploy.yml`. Workflow запускается при push в `main`, подключается к серверу по SSH через GitHub Secrets:

```text
DEPLOY_KEY
SERVER_HOST
SERVER_USER
```

и выполняет:

```bash
bash /var/www/worktimesync.ru/deploy.sh
```

## Что показывает MVP на защите

1. Дашборд состояния команды.
2. Список сотрудников и статусы риска.
3. Карточку сотрудника.
4. Конфликты вне рабочего времени.
5. Командную доступность.
6. Лучшие слоты встречи.
7. Рекомендации.
8. Уведомления как следующий слой действий.
9. Группы сотрудников по проблемам.
10. Swagger backend с полным API.
11. Загрузку CSV/JSON как основу для дальнейшей интеграции.

## Что можно развить после MVP

- Подключить PostgreSQL или SQLite вместо файлов.
- Добавить авторизацию и реальные роли.
- Подключить Google Calendar.
- Подключить HRM.
- Подключить task-tracker.
- Добавить историю изменений графиков.
- Добавить AI-ассистента поверх рассчитанных метрик.
- Добавить реальные push/email/Telegram-уведомления.
- Добавить отдельные frontend-страницы для groups, notifications и risk explanation.
