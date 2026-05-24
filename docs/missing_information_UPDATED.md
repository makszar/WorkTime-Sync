# Missing information и задачи следующего этапа WorkTime Sync

Файл фиксирует текущее состояние проекта после backend V2.2 и список того, что нужно доделать дальше.

---

## 1. Текущее состояние

| Область | Статус |
|---|---|
| Backend V2.2 | роли, scope, tasks, confirmations, company/hr endpoints уже добавлены |
| Frontend | пока в основном старый MVP под руководителя отдела |
| Данные | базовые данные есть, но мало данных для красивого demo workflow |
| Задачи | общий механизм задач есть |
| Задачи по встречам | не доработаны как отдельный сценарий |
| Личный кабинет сотрудника | backend endpoint есть, frontend UI нет |
| HR-dashboard | backend endpoint есть, frontend UI нет |
| Executive dashboard | backend endpoint есть, frontend UI нет |
| Реальные уведомления | нет, пока только задачи/уведомления внутри API |
| Production-auth | нет |
| База данных | нет, используются CSV/JSON |

---

## 2. Главная цель следующего этапа

Нужно визуально и логически соединить backend V2.2 с frontend.

```text
руководитель/HR входит в ЛК
   ↓
видит сотрудников и проблемы
   ↓
создаёт задачу сотруднику
   ↓
сотрудник входит в личный кабинет
   ↓
видит задачу
   ↓
подтверждает, отклоняет или комментирует
   ↓
руководитель/HR видит обновлённый статус
```

Дополнительно нужно добавить задачи по встречам:

```text
событие в календаре → конфликт/планирование встречи → задача сотруднику → подтверждение/перенос/согласование
```

---

# 3. Задачи для frontend

## 3.1. Обновить frontend API client

**Файл:** `frontend/src/api/worktimeApi.js`

Сейчас frontend всё ещё грузит данные в основном через department. Нужно перейти на `user_id`:

```text
/api/worktime/overview?user_id=<user.id>
```

Добавить функции:

```js
export async function loadWorktimeData(user) {}
export async function loadCompanyAnalytics(user) {}
export async function loadHrDashboard(user) {}
export async function loadEmployeeCabinet(user) {}
export async function loadTasks(user, filters = {}) {}
export async function loadMyTasks(user) {}
export async function createTask(user, payload) {}
export async function updateTaskStatus(user, taskId, payload) {}
export async function confirmSchedule(user, employeeId, payload) {}
export async function loadRiskExplanation(user, employeeId) {}
```

Важно: старую работу через `department` можно оставить как fallback.

## 3.2. Добавить role-based routing

**Файлы:**

```text
frontend/src/App.jsx
frontend/src/components/Layout.jsx
```

После login frontend должен смотреть:

```js
user.role
user.scope
user.department
user.employee_id
```

| Role | Главная страница |
|---|---|
| `executive` | `ExecutiveDashboard` |
| `hr` | `HRDashboard` |
| `department_manager` | текущий `Dashboard` отдела |
| `employee` | `EmployeeCabinet` |

## 3.3. Обновить экран входа

Сейчас экран входа подписан как вход руководителя отдела. Нужно изменить текст, потому что теперь есть 4 роли.

Добавить подсказку с demo-аккаунтами:

| Роль | Логин | Пароль |
|---|---|---|
| Полный руководитель | `executive_demo` | `test0` |
| HR | `hr_demo` | `testhr` |
| Руководитель Core Platform | `zarix` | `i9VUibm6` |
| Сотрудник Core Platform | `gleb_employee` | `emp5` |

## 3.4. ExecutiveDashboard

**Новый файл:** `frontend/src/pages/ExecutiveDashboard.jsx`

Показывать:

- все отделы;
- количество сотрудников;
- средний риск по компании;
- количество конфликтов;
- среднюю загрузку;
- топ сотрудников по риску;
- сравнение отделов;
- задачи по компании;
- переход в конкретный отдел.

Backend endpoint:

```text
GET /analytics/company?user_id=u0
```

## 3.5. HRDashboard

**Новый файл:** `frontend/src/pages/HRDashboard.jsx`

Показывать:

- HR/data mismatches;
- timezone conflicts;
- устаревшие графики;
- сотрудники без подтверждения;
- schedule confirmations;
- задачи HR;
- data-quality;
- кнопку создания HR-задачи.

Backend endpoint:

```text
GET /analytics/hr-dashboard?user_id=u_hr
```

## 3.6. EmployeeCabinet

**Новый файл:** `frontend/src/pages/EmployeeCabinet.jsx`

Показывать:

| Блок | Содержимое |
|---|---|
| Мой профиль | имя, отдел, роль, формат работы |
| Мой график | дни, часы, timezone |
| Мои метрики | актуальность, загрузка, риск |
| Мои события | встречи и конфликты |
| Мои задачи | pending/confirmed/rejected/done |
| Подтверждение графика | статус и кнопка подтверждения |
| Комментарий | поле для комментария при подтверждении/отклонении |

Backend endpoints:

```text
GET /employees/me?user_id=emp5
GET /tasks/my?user_id=emp5
PATCH /employees/5/confirm-schedule?user_id=emp5
PATCH /tasks/{task_id}/status?user_id=emp5
```

## 3.7. UI задач для руководителя отдела

В текущий интерфейс руководителя отдела добавить:

- список задач отдела;
- фильтр по статусу;
- кнопку “Создать задачу”;
- кнопку “Запросить подтверждение графика”;
- кнопку “Создать задачу по встрече”;
- статус задач в карточке сотрудника.

Backend endpoints:

```text
GET /tasks?user_id=u1
POST /tasks?user_id=u1
PATCH /tasks/{task_id}/status?user_id=u1
```

## 3.8. UI задач по встречам

Нужно добавить сценарии:

| Сценарий | Действие |
|---|---|
| Встреча вне рабочего времени | создать задачу `meeting_outside_work_approval` |
| Нужно подтвердить участие | создать задачу `meeting_confirmation` |
| Нужно перенести встречу | создать задачу `reschedule_meeting` |

В карточке задачи показывать:

- тип задачи;
- сотрудника;
- связанную встречу;
- время встречи;
- причину;
- статус;
- комментарий сотрудника.

## 3.9. Компоненты

Добавить компоненты:

```text
frontend/src/components/TaskCard.jsx
frontend/src/components/TaskForm.jsx
frontend/src/components/TaskStatusBadge.jsx
frontend/src/components/RoleBadge.jsx
frontend/src/components/TaskTypeBadge.jsx
frontend/src/components/ScheduleConfirmationCard.jsx
```

## 3.10. Не ломать текущий frontend

Сохранить:

- текущий Dashboard;
- Employees;
- EmployeeProfile;
- Conflicts;
- Availability;
- Recommendations;
- fallback на mock;
- работу с `department`, если backend старой версии.

---

# 4. Задачи по данным для backend и frontend

## 4.1. Расширить users.json

Сейчас employee-аккаунтов только 3. Для демо мало.

| Что | Минимум | Лучше |
|---|---:|---:|
| employee-аккаунты | 10 | 25 |
| employee-аккаунты на отдел | 2 | 5 |

Рекомендация: добавить аккаунты для всех 25 сотрудников.

## 4.2. Расширить tasks.json

Сейчас задач только 3, все `pending`. Нужно добавить 12–15 задач.

| Тип | Сколько | Статусы |
|---|---:|---|
| `confirm_schedule` | 3–4 | pending/confirmed |
| `review_hr_profile` | 2–3 | pending/rejected |
| `review_load` | 2–3 | pending/done |
| `meeting_confirmation` | 2–3 | pending/confirmed |
| `reschedule_meeting` | 2–3 | pending/rejected |
| `meeting_outside_work_approval` | 2–3 | pending/confirmed |

## 4.3. Добавить related_event_id для задач по встречам

Для задач по встречам добавить поле:

```json
"related_event_id": 12
```

Зачем:

- frontend сможет показать, к какой встрече относится задача;
- backend сможет проверить, существует ли событие;
- сотрудник увидит время и название встречи.

## 4.4. Расширить schedule_confirmations.json

Сейчас подтверждений мало. Нужно добавить 10–15 записей.

| Статус | Что означает |
|---|---|
| `confirmed` | график подтверждён |
| `pending` | ожидает подтверждения |
| `rejected` | сотрудник не согласен |
| `change_requested` | сотрудник просит изменить график |

## 4.5. Добавить данные для красивого demo

| Сценарий | Данные |
|---|---|
| руководитель назначает задачу сотруднику | task `confirm_schedule` |
| HR назначает задачу | task `review_hr_profile` |
| сотрудник подтверждает график | schedule confirmation |
| сотрудник отклоняет задачу | task `rejected` + comment |
| встреча вне рабочего времени | event + task `meeting_outside_work_approval` |
| перенос встречи | event + task `reschedule_meeting` |
| подтверждение встречи | event + task `meeting_confirmation` |

---

# 5. Задачи для backend

## 5.1. Добавить допустимые типы задач

**Файлы:**

```text
backend/app/models.py
backend/app/main.py
```

Разрешённые типы:

```text
confirm_schedule
review_hr_profile
review_load
update_timezone
meeting_confirmation
reschedule_meeting
meeting_outside_work_approval
```

Если приходит неизвестный type — возвращать `400`.

## 5.2. Добавить задачи по встречам

Расширить модель задачи:

| Поле | Назначение |
|---|---|
| `related_event_id` | id события из `events.csv` |
| `meeting_action` | confirm / reschedule / approve_outside_work |
| `suggested_start_datetime` | новое время, если предлагается перенос |
| `suggested_end_datetime` | новое время, если предлагается перенос |

Для MVP достаточно `related_event_id`.

## 5.3. Проверять related_event_id

При создании задачи по встрече backend должен проверить:

1. `related_event_id` существует;
2. событие относится к тому же сотруднику;
3. руководитель отдела имеет доступ к этому сотруднику;
4. если задача `meeting_outside_work_approval`, событие реально вне рабочего времени;
5. если задача `reschedule_meeting`, событие существует и может быть перенесено;
6. если задача `meeting_confirmation`, событие связано с сотрудником.

## 5.4. Обновить TaskCreateRequest

Добавить поля:

```python
related_event_id: int | None = None
meeting_action: str | None = None
suggested_start_datetime: str | None = None
suggested_end_datetime: str | None = None
```

## 5.5. Обновить create_task

В `POST /tasks` добавить:

- валидацию `type`;
- валидацию `related_event_id`;
- сохранение новых полей;
- понятные ошибки;
- автоматическое заполнение department по сотруднику;
- запрет руководителю отдела создавать задачу сотруднику другого отдела.

## 5.6. Обновить update_task_status

Для задач по встречам:

| Статус | Что делать |
|---|---|
| `confirmed` | сотрудник согласился |
| `rejected` | сотрудник не согласен, нужен комментарий |
| `done` | руководитель/HR закрыл задачу |
| `reschedule_requested` | сотрудник просит другое время |

Добавить проверку: при `rejected` или `reschedule_requested` комментарий обязателен.

## 5.7. Расширить /tasks и /tasks/my

В ответ задач добавить:

- `employee_name`;
- `employee_role`;
- `department`;
- `related_event`;
- `creator_name`;
- `creator_role_label`.

Это упростит frontend, чтобы ему не приходилось склеивать данные вручную.

## 5.8. Обновить /employees/me

В личный кабинет сотрудника добавить:

- pending tasks;
- completed tasks;
- scheduleConfirmationStatus;
- tasks by type;
- upcoming/conflicting events;
- meeting tasks.

## 5.9. Обновить /analytics/hr-dashboard

Добавить:

- сотрудники без подтверждения;
- задачи HR;
- просроченные задачи;
- rejected tasks;
- change_requested confirmations;
- HR mismatch с открытой задачей или без неё.

## 5.10. Обновить /analytics/company

Добавить:

- задачи по отделам;
- количество pending tasks;
- количество rejected tasks;
- процент подтверждённых графиков;
- отделы с худшей подтверждаемостью;
- отделы с большим количеством встреч вне рабочего времени.

## 5.11. Обновить data-quality

Проверять:

| Проверка | Что ловит |
|---|---|
| orphan tasks | задача на несуществующего сотрудника |
| orphan related_event_id | задача с несуществующей встречей |
| task-event mismatch | задача по встрече не того сотрудника |
| invalid task status | неизвестный статус |
| invalid task type | неизвестный тип |
| orphan confirmations | подтверждение для несуществующего сотрудника |
| duplicate confirmations | несколько подтверждений одного сотрудника |

## 5.12. Обновить backend-тесты

Добавить тесты:

| Тест | Что проверяет |
|---|---|
| create meeting task | руководитель создаёт задачу по встрече |
| manager cannot assign outside department | руководитель не может назначить чужому отделу |
| employee sees meeting task | сотрудник видит свою задачу по встрече |
| employee confirms meeting task | статус меняется на confirmed |
| employee rejects with comment | rejected требует комментарий |
| related_event_id validation | несуществующее событие даёт 400 |
| task-event mismatch | событие другого сотрудника даёт 400 |
| data-quality tasks | ловит ошибки в tasks.json |
| company analytics tasks | считает задачи по компании |
| HR dashboard task statuses | показывает rejected/pending/overdue |

---

# 6. Оставшиеся missing проекта

## 6.1. Frontend не подключен к backend V2.2 полностью

Нужно подключить:

- `user_id`;
- roles;
- tasks;
- confirmations;
- `/employees/me`;
- `/analytics/company`;
- `/analytics/hr-dashboard`.

## 6.2. Нет production-авторизации

Сейчас:

- пароли в JSON;
- demo-token;
- нет JWT;
- нет refresh/session.

## 6.3. Нет базы данных

Сейчас CSV/JSON. Дальше: SQLite для MVP+, PostgreSQL для production.

## 6.4. Нет реальных интеграций

| Источник | Реальная интеграция |
|---|---|
| календарь | Google Calendar / Outlook |
| HR | HRM |
| задачи | Jira / YouTrack |
| уведомления | email / Telegram / Slack |

## 6.5. Нет реальных уведомлений

Сейчас задачи отображаются через API, но не отправляются автоматически. Дальше: уведомления в интерфейсе, email, Telegram, Slack/Teams.

## 6.6. Нет полной истории изменений

Нужно хранить:

- кто создал задачу;
- кто изменил статус;
- когда;
- старое/новое значение;
- комментарий;
- историю подтверждений графика.

## 6.7. Нет AI-ассистента

Сейчас есть risk explanation и рекомендации. Возможное развитие: объяснять риск, советовать, кому назначить задачу, выбирать лучший слот встречи, формировать сообщение сотруднику.

---

## 7. Приоритеты

### Высокий приоритет

1. Подключить frontend к `user_id`.
2. Сделать EmployeeCabinet.
3. Сделать UI задач.
4. Сделать создание задач руководителем/HR.
5. Добавить задачи по встречам в backend.
6. Расширить synthetic data.

### Средний приоритет

1. ExecutiveDashboard.
2. HRDashboard.
3. Расширенная data-quality.
4. Тесты задач по встречам.
5. Красивые статусы и бейджи.

### Низкий приоритет

1. Реальные интеграции.
2. Production-auth.
3. База данных.
4. Реальные уведомления.
5. AI-ассистент.
