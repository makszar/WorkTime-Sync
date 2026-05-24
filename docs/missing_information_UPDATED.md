# Missing information WorkTime Sync — финальные задачи для завершения MVP

Документ фиксирует **окончательный список того, чего ещё не хватает**, чтобы закрыть текущий MVP WorkTime Sync после обновлений backend/data до версии V2.4.

Цель этого файла — дать команде понятные инструкции: что нужно доделать во frontend, что осталось в backend, что нужно проверить по данным, и что уже можно считать реализованным.

---

## 1. Текущее состояние проекта

### 1.1. Что уже реализовано

| Блок | Статус |
|---|---|
| FastAPI backend | реализовано |
| Backend V2.4.0 | реализовано |
| Demo-login | реализовано |
| Demo-token `Authorization: Bearer demo-...` | реализовано |
| Роли пользователей | реализовано |
| Scope-доступ по ролям | реализовано |
| Полный руководитель `executive` | реализовано на уровне backend/data |
| HR `hr` | реализовано на уровне backend/data |
| Руководители отделов `department_manager` | реализовано |
| Сотрудники `employee` | реализовано |
| Аккаунты для всех 25 сотрудников | реализовано |
| `tasks.json` | реализовано |
| `schedule_confirmations.json` | реализовано |
| Задачи по встречам | реализовано на уровне backend/data |
| `related_event_id` | реализовано |
| Проверка связи задачи и события | реализовано |
| Подтверждение графика | реализовано на уровне backend |
| `/employees/me` | реализовано |
| `/tasks`, `/tasks/my` | реализовано |
| `/analytics/company` | реализовано |
| `/analytics/hr-dashboard` | реализовано |
| Risk weights по отделам | реализовано |
| Data-quality для основных данных | реализовано |
| Frontend login | реализовано |
| Frontend API через `user_id` | частично реализовано |
| Frontend нормализация `tasks`, `taskStatusCounts`, `currentUser`, `meta` | частично реализовано |

---

## 2. Главный вывод по текущему состоянию

Backend и synthetic data уже в целом закрывают новую логику MVP:

```text
роли → доступ → задачи → подтверждения → задачи по встречам → аналитика по компании/HR
```

Главный незакрытый блок сейчас — **frontend**. Многие возможности уже есть в API, но пользователь пока не видит их в интерфейсе.

Текущий frontend всё ещё в основном работает как старый MVP:

```text
Dashboard
Employees
EmployeeProfile
Conflicts
Availability
Recommendations
```

Нужно вывести новые backend-возможности на экран.

---

# 3. Финальные задачи для frontend

## 3.1. Обновить экран входа

### Проблема

Сейчас экран входа всё ещё подписан как вход руководителя отдела, хотя теперь есть 4 типа ролей:

```text
executive
hr
department_manager
employee
```

### Что сделать

В `frontend/src/App.jsx` или отдельном компоненте login:

1. заменить текст “Вход руководителя отдела”;
2. написать, что доступно 4 роли;
3. добавить подсказки с demo-аккаунтами;
4. показать пользователю, что можно войти не только руководителем, но и HR/сотрудником.

### Рекомендуемый текст

```text
Вход в WorkTime Sync

В демо доступны роли:
полный руководитель, HR, руководитель отдела и сотрудник.
```

### Demo-аккаунты для подсказки

| Роль | Логин | Пароль |
|---|---|---|
| Полный руководитель | `executive_demo` | `test0` |
| HR | `hr_demo` | `testhr` |
| Руководитель Core Platform | `zarix` | `i9VUibm6` |
| Руководитель Product UI | `lixxxa` | `test1` |
| Руководитель People Ops | `baftype` | `test2` |
| Руководитель Delivery | `ssdshkaaa` | `test3` |
| Руководитель Quality | `agentemy` | `test4` |
| Сотрудник 1 | `employee1` | `emp1` |
| Сотрудник 5 / demo | `employee5` или `gleb_employee` | `emp5` |
| Сотрудник 25 | `employee25` | `emp25` |

### Критерий готовности

Пользователь на экране входа понимает, что система поддерживает разные роли, а не только руководителя отдела.

---

## 3.2. Сделать role-based routing

### Проблема

После login frontend сейчас всё равно открывает старый `dashboard`.

### Что сделать

После авторизации смотреть:

```js
user.role
user.scope
user.department
user.employee_id
```

И открывать нужный интерфейс.

### Логика маршрутизации

| `user.role` | Главный экран |
|---|---|
| `executive` | `ExecutiveDashboard` |
| `hr` | `HRDashboard` |
| `department_manager` | текущий `Dashboard` отдела |
| `employee` | `EmployeeCabinet` |

### Где менять

```text
frontend/src/App.jsx
frontend/src/components/Layout.jsx
```

### Критерий готовности

При входе под разными demo-аккаунтами открываются разные интерфейсы.

---

## 3.3. Доработать frontend API client

### Проблема

`worktimeApi.js` уже начал работать через `user_id`, но в нём ещё нет полного набора функций для новых сценариев.

### Что добавить

Файл:

```text
frontend/src/api/worktimeApi.js
```

Добавить функции:

```js
export async function loadCompanyAnalytics(user) {}
export async function loadHrDashboard(user) {}
export async function loadEmployeeCabinet(user) {}
export async function loadTasks(user, filters = {}) {}
export async function loadMyTasks(user) {}
export async function loadTaskMeta(user) {}
export async function createTask(user, payload) {}
export async function updateTaskStatus(user, taskId, payload) {}
export async function confirmSchedule(user, employeeId, payload) {}
export async function loadRiskExplanation(user, employeeId) {}
```

### Как лучше отправлять авторизацию

Backend поддерживает два варианта:

```text
?user_id=<user.id>
```

и

```http
Authorization: Bearer demo-...
```

Для frontend лучше использовать token, который приходит после login:

```js
headers: {
  Authorization: `Bearer ${user.token}`
}
```

`user_id` можно оставить как fallback.

### Критерий готовности

Frontend умеет обращаться ко всем новым backend endpoint’ам:

```text
/employees/me
/tasks
/tasks/my
/tasks/meta
/analytics/company
/analytics/hr-dashboard
/employees/{id}/confirm-schedule
/tasks/{id}/status
```

---

## 3.4. Сделать ExecutiveDashboard

### Назначение

Экран полного руководителя показывает общую картину по компании.

### Файл

```text
frontend/src/pages/ExecutiveDashboard.jsx
```

### Backend endpoint

```text
GET /analytics/company
Authorization: Bearer demo-executive_demo
```

или:

```text
GET /analytics/company?user_id=u0
```

### Что показывать

| Блок | Что внутри |
|---|---|
| Общая сводка | количество сотрудников, средний риск, конфликты |
| Отделы | сравнение отделов |
| Риски | топ сотрудников/отделов с высоким риском |
| Задачи | pending/rejected/done по компании |
| Подтверждения | процент подтверждённых графиков |
| Проблемные отделы | худшая подтверждаемость, много встреч вне графика |

### Критерий готовности

Полный руководитель видит данные **по всем отделам**, а не только по одному department.

---

## 3.5. Сделать HRDashboard

### Назначение

Экран HR показывает качество и актуальность кадровых данных.

### Файл

```text
frontend/src/pages/HRDashboard.jsx
```

### Backend endpoint

```text
GET /analytics/hr-dashboard
Authorization: Bearer demo-hr_demo
```

или:

```text
GET /analytics/hr-dashboard?user_id=u_hr
```

### Что показывать

| Блок | Что внутри |
|---|---|
| HR-расхождения | mismatch по графику, timezone, формату |
| Подтверждения | confirmed/pending/rejected/change_requested |
| Задачи HR | pending/rejected/overdue |
| Сотрудники без подтверждения | список |
| Data-quality | ошибки и предупреждения |
| Действия | создать HR-задачу |

### Критерий готовности

HR видит не проектную нагрузку как руководитель отдела, а именно HR-проблемы: актуальность графиков, расхождения, подтверждения, отклонения.

---

## 3.6. Сделать EmployeeCabinet

### Назначение

Личный кабинет сотрудника — ключевой экран новой логики.

### Файл

```text
frontend/src/pages/EmployeeCabinet.jsx
```

### Backend endpoint

```text
GET /employees/me
Authorization: Bearer demo-employee5
```

или:

```text
GET /employees/me?user_id=emp5
```

### Что показывать

| Блок | Что внутри |
|---|---|
| Мой профиль | имя, отдел, роль, формат работы |
| Мой график | рабочие дни, часы, timezone |
| Моя актуальность | `schedule_actuality`, дата обновления |
| Мой риск | risk, risk status, объяснение |
| Мои события | upcoming events |
| Мои конфликты | conflicting events |
| Мои задачи | pending/completed/meeting tasks |
| Подтверждение графика | текущий статус + кнопка |
| Комментарий | поле для подтверждения/отклонения |

### Кнопки

| Кнопка | Endpoint |
|---|---|
| Подтвердить график | `PATCH /employees/{employee_id}/confirm-schedule` |
| Подтвердить задачу | `PATCH /tasks/{task_id}/status` |
| Отклонить задачу | `PATCH /tasks/{task_id}/status` |
| Запросить перенос | `PATCH /tasks/{task_id}/status` со статусом `reschedule_requested` |

### Критерий готовности

Сотрудник входит в систему и видит **только свои данные**, свои задачи и свои встречи.

---

## 3.7. Сделать UI задач

### Что нужно

Добавить отдельный UI для задач во всех ролях:

| Роль | Что видит |
|---|---|
| Executive | задачи по всей компании |
| HR | HR-задачи и статусы |
| Руководитель отдела | задачи своего отдела |
| Сотрудник | только свои задачи |

### Компоненты

Создать:

```text
frontend/src/components/TaskCard.jsx
frontend/src/components/TaskForm.jsx
frontend/src/components/TaskStatusBadge.jsx
frontend/src/components/TaskTypeBadge.jsx
frontend/src/components/RoleBadge.jsx
frontend/src/components/ScheduleConfirmationCard.jsx
```

### TaskCard должен показывать

| Поле | Отображение |
|---|---|
| `title` | название задачи |
| `type` | тип задачи |
| `status` | бейдж статуса |
| `employee_name` | кому назначена |
| `creator_name` | кто назначил |
| `department` | отдел |
| `due_date` | срок |
| `employee_comment` | комментарий |
| `related_event` | связанная встреча, если есть |
| `suggested_start_datetime` | предложенное время переноса |
| `suggested_end_datetime` | предложенное время переноса |

### Критерий готовности

Задачи отображаются понятно и не требуют открытия Swagger.

---

## 3.8. Сделать создание задач из интерфейса

### Кто может создавать задачи

| Роль | Кому может назначать |
|---|---|
| `executive` | любому сотруднику |
| `hr` | любому сотруднику |
| `department_manager` | только сотрудникам своего отдела |
| `employee` | не может создавать задачи |

### Backend endpoint

```text
POST /tasks
```

### UI

В карточке сотрудника или списке задач добавить кнопку:

```text
Создать задачу
```

### Поля формы

| Поле | Обязательно? |
|---|---|
| сотрудник | да |
| тип задачи | да |
| title | да |
| description | да |
| due_date | да |
| related_event_id | только для задач по встречам |
| meeting_action | только для задач по встречам |
| suggested_start_datetime | для `reschedule_meeting` |
| suggested_end_datetime | для `reschedule_meeting` |

### Критерий готовности

Руководитель отдела может создать задачу сотруднику своего отдела, но не может назначить задачу сотруднику чужого отдела.

---

## 3.9. Сделать задачи по встречам в UI

### Уже есть на backend

Backend уже поддерживает:

```text
meeting_confirmation
reschedule_meeting
meeting_outside_work_approval
related_event_id
meeting_action
suggested_start_datetime
suggested_end_datetime
```

### Что нужно во frontend

При создании задачи по встрече:

1. выбрать сотрудника;
2. показать его события;
3. выбрать событие;
4. выбрать тип задачи;
5. передать `related_event_id`;
6. для переноса передать новое время.

### Типы задач по встречам

| Тип | Когда использовать |
|---|---|
| `meeting_confirmation` | нужно подтвердить участие |
| `reschedule_meeting` | нужно согласовать перенос |
| `meeting_outside_work_approval` | встреча вне рабочего времени |

### Критерий готовности

Руководитель может из интерфейса создать задачу по конкретной встрече, а сотрудник увидит её в личном кабинете с названием/временем встречи.

---

## 3.10. Сделать подтверждение/отклонение задач сотрудником

### Endpoint

```text
PATCH /tasks/{task_id}/status
```

### Статусы

| Статус | Кто ставит |
|---|---|
| `confirmed` | сотрудник / руководитель / HR |
| `rejected` | сотрудник |
| `reschedule_requested` | сотрудник |
| `done` | руководитель / HR |
| `expired` | система или руководитель/HR |

### Важно

Для статусов:

```text
rejected
reschedule_requested
```

комментарий обязателен.

### Критерий готовности

Сотрудник может подтвердить задачу, отклонить её с комментарием или запросить перенос.

---

## 3.11. Сделать подтверждение графика из интерфейса

### Endpoint

```text
PATCH /employees/{employee_id}/confirm-schedule
```

### Где показывать

В `EmployeeCabinet`:

```text
Статус графика: pending / confirmed / rejected / change_requested
```

Кнопка:

```text
Подтвердить график
```

Поле:

```text
Комментарий
```

### Критерий готовности

Сотрудник может подтвердить график без Swagger, и статус обновляется в интерфейсе.

---

# 4. Финальные задачи для backend

Backend V2.4 уже закрывает большую часть MVP, но остаются задачи, которые нужны для финального завершения workflow.

---

## 4.1. Реально применять решение по задаче встречи

### Проблема

Сейчас задача по встрече может быть создана и подтверждена, но нет отдельного финального действия, которое меняет само событие в `events.csv` после согласованного переноса.

### Что сделать

Добавить endpoint:

```text
POST /tasks/{task_id}/apply
```

или:

```text
PATCH /tasks/{task_id}/apply
```

### Логика

| Тип задачи | Что делает apply |
|---|---|
| `meeting_confirmation` | фиксирует согласие, событие не меняет |
| `meeting_outside_work_approval` | фиксирует согласование встречи вне рабочего времени |
| `reschedule_meeting` | меняет `start_datetime` и `end_datetime` у события |
| `confirm_schedule` | синхронизирует `schedule_confirmations` |
| `review_hr_profile` | только закрывает задачу или оставляет комментарий |
| `review_load` | только закрывает задачу или оставляет комментарий |

### Критерий готовности

Если задача `reschedule_meeting` подтверждена, руководитель может применить перенос, и связанное событие реально меняет время.

---

## 4.2. Добавить save_events()

### Проблема

Для применения переноса встречи нужно сохранять изменённые события.

### Что сделать

В `backend/app/data_loader.py` добавить функцию:

```python
save_events(events)
```

Она должна сохранять обновлённые события обратно в active data source.

### Критерий готовности

После применения переноса событие сохраняется и при следующем запросе возвращается уже с новым временем.

---

## 4.3. Автоматическая генерация задач по проблемным встречам

### Сейчас

Задачи создаются вручную.

### Что добавить

Endpoint или служебную функцию:

```text
POST /tasks/generate-from-conflicts
```

Логика:

1. найти встречи вне рабочего времени;
2. если по встрече ещё нет открытой задачи;
3. создать задачу `meeting_outside_work_approval` или `reschedule_meeting`;
4. назначить её сотруднику;
5. указать `related_event_id`.

### Критерий готовности

Руководитель может одним действием создать задачи по проблемным встречам отдела.

---

## 4.4. Улучшить task history

### Проблема

Сейчас задача хранит только текущий статус и комментарий.

### Что добавить

Добавить историю изменений:

```json
"history": [
  {
    "changed_at": "2026-05-24T15:30:00",
    "changed_by_user_id": "emp5",
    "old_status": "pending",
    "new_status": "confirmed",
    "comment": "Подтверждаю."
  }
]
```

### Критерий готовности

Можно показать, кто и когда подтвердил/отклонил задачу.

---

## 4.5. Расширить data-quality под финальные проверки задач

### Уже есть

Data-quality частично работает с tasks/confirmations.

### Что ещё проверить

| Проверка | Что ловит |
|---|---|
| task без employee | задача назначена несуществующему сотруднику |
| task без creator | задача создана несуществующим пользователем |
| task с чужим related_event_id | событие относится к другому сотруднику |
| meeting task без related_event_id | задача по встрече без встречи |
| reschedule task без suggested datetime | перенос без нового времени |
| duplicate confirmation | несколько подтверждений одного сотрудника |
| confirmation без employee | подтверждение для несуществующего сотрудника |
| invalid confirmation status | неверный статус подтверждения |
| task overdue | просроченная задача |

### Критерий готовности

`/analytics/data-quality` показывает ошибки не только по employees/events/hr_profiles, но и по задачам/подтверждениям.

---

## 4.6. Добавить тесты backend на финальный workflow

Добавить тесты:

| Тест | Что проверяет |
|---|---|
| demo-token auth | API работает через `Authorization` |
| token/user_id mismatch | конфликт token и user_id даёт 403 |
| executive can assign any employee | полный руководитель может назначить всем |
| manager cannot assign outside department | руководитель не может назначить чужому отделу |
| employee sees only own tasks | сотрудник видит только свои задачи |
| meeting task requires related_event_id | задача по встрече требует событие |
| related_event_id must match employee | событие должно относиться к сотруднику |
| reschedule requires suggested range | перенос требует новое время |
| rejected requires comment | отклонение требует комментарий |
| confirm_schedule sync | подтверждение задачи обновляет schedule confirmation |
| task apply reschedule | перенос реально меняет event |
| data-quality detects task errors | data-quality ловит ошибки задач |

---

# 5. Финальные задачи по данным

Данные сейчас сильно улучшены: есть 25 employee-аккаунтов, 24 задачи, 25 подтверждений графика. Остались не критичные, но полезные для финального MVP улучшения.

---

## 5.1. Проверить users.json

### Уже есть

- executive;
- HR;
- 5 руководителей отделов;
- employee1–employee25;
- удобный demo-login `gleb_employee`.

### Что проверить

| Проверка | Ожидаемый результат |
|---|---|
| у каждого employee есть `employee_id` | да |
| `employee_id` существует в employees.csv | да |
| department пользователя совпадает с team сотрудника | да |
| нет дубликатов `id` | желательно |
| нет дубликатов `login`, кроме осознанного demo alias | желательно |
| все пароли подходят для demo | да |

---

## 5.2. Проверить tasks.json

### Уже есть

- разные типы задач;
- разные статусы;
- задачи по встречам;
- `related_event_id`;
- `meeting_action`;
- `suggested_start_datetime`;
- `suggested_end_datetime`.

### Что проверить

| Проверка | Ожидаемый результат |
|---|---|
| у каждой задачи есть employee | да |
| creator существует в users.json | да |
| department задачи совпадает с team сотрудника | да |
| related_event_id существует | для meeting tasks |
| related_event_id относится к тому же employee | да |
| reschedule task имеет suggested datetime | да |
| rejected/reschedule_requested имеют comment | да |

---

## 5.3. Проверить schedule_confirmations.json

### Уже есть

Записи для всех 25 сотрудников.

### Что проверить

| Проверка | Ожидаемый результат |
|---|---|
| employee_id 1–25 покрыты | да |
| нет дублей employee_id | да |
| статус из допустимого списка | да |
| confirmed имеет confirmed_at | да |
| rejected/change_requested имеют comment | желательно |
| pending может иметь пустой confirmed_at | да |

---

## 5.4. Добавить больше реалистичных absent/conflict сценариев

Не обязательно для MVP, но полезно для защиты:

| Сценарий | Зачем |
|---|---|
| встреча во время больничного | показать conflict с absence |
| встреча в отпуске | показать data/availability конфликт |
| сотрудник в другом timezone | показать timezone mismatch |
| сотрудник с неполной неделей | показать нестандартный график |
| перегруз QA перед релизом | показать риск Quality |
| Delivery-сотрудник с переносом встречи | показать meeting workflow |

---

# 6. Что не нужно делать до завершения MVP

Чтобы не распыляться, эти задачи лучше оставить на развитие после MVP:

| Задача | Почему не сейчас |
|---|---|
| Полноценный JWT | demo-token достаточно для защиты |
| PostgreSQL | CSV/JSON достаточно для MVP |
| Реальная интеграция Google Calendar | synthetic events закрывают кейс |
| Реальная HRM-интеграция | synthetic HR profiles закрывают кейс |
| Telegram/email уведомления | задачи в интерфейсе достаточно |
| AI-chat assistant | risk explanation уже закрывает базовое объяснение |
| Полная история аудита | можно добавить позже |
| Сложный таск-трекер | tasks.json достаточно для MVP |

---

# 7. Финальный чек-лист завершения MVP

## Frontend

| Задача | Статус |
|---|---|
| Обновить login под 4 роли | нужно сделать |
| Role-based routing | нужно сделать |
| ExecutiveDashboard | нужно сделать |
| HRDashboard | нужно сделать |
| EmployeeCabinet | нужно сделать |
| UI задач | нужно сделать |
| Создание задач | нужно сделать |
| Подтверждение/отклонение задач | нужно сделать |
| Подтверждение графика | нужно сделать |
| UI задач по встречам | нужно сделать |
| Отображение related_event | нужно сделать |
| Использование demo-token | желательно сделать |

## Backend

| Задача | Статус |
|---|---|
| Роли и scope | сделано |
| Demo-token | сделано |
| Tasks API | сделано |
| Meeting tasks | сделано |
| Schedule confirmations | сделано |
| Company analytics | сделано |
| HR dashboard API | сделано |
| Применение решения по задаче встречи | нужно сделать |
| `save_events()` | нужно сделать |
| Автогенерация задач по конфликтным встречам | желательно сделать |
| Task history | желательно сделать |
| Финальные tests | нужно сделать |

## Data

| Задача | Статус |
|---|---|
| 25 employee accounts | сделано |
| 24 tasks | сделано |
| 25 confirmations | сделано |
| meeting tasks | сделано |
| проверить консистентность users/tasks/confirmations | нужно проверить |
| добавить больше absence/conflict сценариев | желательно |

---

# 8. Минимум, который нужно сделать перед финальной защитой

Если времени мало, обязательно закрыть только это:

1. `EmployeeCabinet`;
2. отображение задач сотрудника;
3. подтверждение/отклонение задачи;
4. подтверждение графика;
5. создание задачи руководителем отдела;
6. отображение задачи по встрече с `related_event`;
7. обновить экран входа под 4 роли;
8. проверить, что executive/HR/manager/employee видят разные данные;
9. проверить backend tests.

После этого MVP можно считать завершённым и переходить к развитию.
