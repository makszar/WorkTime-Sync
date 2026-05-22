# Missing information и задачи следующего этапа WorkTime Sync

Этот файл фиксирует, что уже реализовано, что отсутствует, и какие задачи нужно передать frontend/backend-команде на следующий этап.

---

## 1. Краткое состояние проекта

| Область | Статус |
|---|---|
| Frontend | React + Vite, основные экраны MVP реализованы |
| Backend | FastAPI, аналитика и API реализованы |
| Данные | `data/synthetic/*.csv` |
| Login | demo-login реализован |
| Department-фильтр | реализован |
| Риски/конфликты/доступность | реализованы |
| Recommendations/notifications | реализованы в backend/API |
| Личный кабинет сотрудника | не реализован |
| Полный руководитель | не реализован отдельным интерфейсом |
| HR-dashboard | не реализован отдельным интерфейсом |
| Задачи от руководителя/HR | не реализованы |
| Подтверждение графика сотрудником | не реализовано |
| Риск с весами отделов | не реализован, сейчас формула общая |
| Production-БД | не реализована |
| Реальные интеграции | не реализованы |

---

## 2. Главная новая задача после митапа

Нужно развить проект из аналитического дашборда в систему взаимодействия ролей:

```text
аналитика → задача → подтверждение сотрудником → актуализация графика
```

Новая логика должна быть такой:

1. полный руководитель видит всю компанию;
2. руководитель отдела видит только свой отдел;
3. HR видит все отделы, но с фокусом на HR-данные, подтверждения и расхождения;
4. сотрудник видит только свой личный кабинет;
5. руководитель/HR может создать задачу сотруднику;
6. сотрудник подтверждает задачу, отклоняет её или оставляет комментарий;
7. статус возвращается руководителю/HR.

---

## 3. Роли и права доступа

| Роль | Scope | Что видит | Что делает |
|---|---|---|---|
| `executive` | `all` | все отделы и всех сотрудников | смотрит глобальную аналитику и сравнение отделов |
| `department_manager` | `department` | только свой отдел | создаёт задачи сотрудникам, контролирует графики и нагрузку |
| `hr` | `all` | всех сотрудников с HR-фокусом | проверяет HR-расхождения, графики, timezone, подтверждения |
| `employee` | `self` | только себя | подтверждает график, отвечает на задачи, оставляет комментарии |

---

# 4. Задачи для backend

## 4.1. Расширить users.json

**Файл:** `data/synthetic/users.json`

Нужно добавить/обновить поля:

| Поле | Обязательно? | Назначение |
|---|---|---|
| `id` | да | id пользователя |
| `login` | да | логин |
| `password` | да | пароль для demo |
| `name` | да | имя |
| `role` | да | `executive`, `department_manager`, `hr`, `employee` |
| `scope` | да | `all`, `department`, `self` |
| `department` | для manager/employee | отдел |
| `employee_id` | для employee | связь с employees.csv |

**Важно:** существующие руководители отделов должны продолжить работать.

---

## 4.2. Добавить role/scope-фильтрацию

**Файл:** `backend/app/main.py`

Сейчас есть фильтр по department. Нужно расширить его до role/scope.

Предлагаемая функция:

```python
def apply_user_scope(user, employees, events, hr_profiles, absences):
    ...
```

Логика:

| Role | Данные |
|---|---|
| `executive` | все данные |
| `hr` | все данные |
| `department_manager` | только `employee.team == user.department` |
| `employee` | только `employee.id == user.employee_id` |

Для MVP можно передавать данные пользователя через query-параметры. JWT пока не обязателен.

---

## 4.3. Добавить tasks dataset

**Файл:** `data/synthetic/tasks.json` или `data/synthetic/tasks.csv`

Минимальная структура задачи:

| Поле | Тип | Назначение |
|---|---|---|
| `id` | int/string | id задачи |
| `employee_id` | int | кому назначена |
| `created_by_user_id` | string | кто создал |
| `created_by_role` | string | роль создателя |
| `department` | string | отдел |
| `type` | string | тип задачи |
| `title` | string | название |
| `description` | string | описание |
| `due_date` | string | срок |
| `status` | string | pending / confirmed / rejected / done / expired |
| `employee_comment` | string | комментарий сотрудника |
| `created_at` | string | дата создания |
| `updated_at` | string | дата обновления |

Типы задач:

| Type | Назначение |
|---|---|
| `confirm_schedule` | подтвердить график |
| `review_hr_profile` | проверить HR-данные |
| `reschedule_meeting` | перенести встречу |
| `review_load` | проверить перегрузку |
| `update_timezone` | обновить часовой пояс |

---

## 4.4. Добавить task API

Новые endpoint’ы:

| Endpoint | Метод | Кто использует | Назначение |
|---|---|---|---|
| `/tasks` | GET | executive, HR, manager | список задач с фильтрацией |
| `/tasks/my` | GET | employee | задачи текущего сотрудника |
| `/tasks` | POST | executive, HR, manager | создать задачу |
| `/tasks/{task_id}` | GET | все роли по правам | открыть задачу |
| `/tasks/{task_id}/status` | PATCH | employee / creator | сменить статус |
| `/employees/{employee_id}/confirm-schedule` | PATCH | employee / HR | подтвердить график |

---

## 4.5. Добавить подтверждение графика

Endpoint:

```text
PATCH /employees/{employee_id}/confirm-schedule
```

Что должен делать:

- фиксировать дату подтверждения;
- закрывать задачу типа `confirm_schedule`, если она есть;
- сохранять комментарий сотрудника, если передан;
- возвращать обновлённый статус подтверждения.

---

## 4.6. Добавить риск с весами по отделам

**Файл:** `backend/app/analytics.py`

Актуальность графика не менять:

```text
A = max(0, 1 - days_since_update / 90)
```

Риск:

```text
R = wA * (1 - A)
  + wC * C
  + wL * L
  + wT * timezone_mismatch
  + wH * hr_mismatch
```

Веса:

| Отдел | `wA` | `wC` | `wL` | `wT` | `wH` |
|---|---:|---:|---:|---:|---:|
| Core Platform | 0.25 | 0.25 | 0.30 | 0.10 | 0.10 |
| Product UI | 0.25 | 0.30 | 0.25 | 0.10 | 0.10 |
| People Ops | 0.30 | 0.15 | 0.20 | 0.10 | 0.25 |
| Delivery | 0.20 | 0.30 | 0.30 | 0.10 | 0.10 |
| Quality | 0.20 | 0.25 | 0.35 | 0.10 | 0.10 |

Fallback для неизвестного отдела:

```text
0.30, 0.25, 0.25, 0.10, 0.10
```

---

## 4.7. Расширить risk explanation

Endpoint:

```text
GET /employees/{employee_id}/risk-explanation
```

Добавить в ответ:

| Поле | Зачем |
|---|---|
| `department` | отдел сотрудника |
| `weights` | веса риска для отдела |
| `departmentLogic` | краткое объяснение весов отдела |
| `formulaWithWeights` | формула с конкретными весами |
| `scheduleConfirmationStatus` | подтверждён ли график |

---

# 5. Задачи для frontend

## 5.1. Добавить routing по ролям

**Файлы:**

```text
frontend/src/App.jsx
frontend/src/components/Layout.jsx
frontend/src/api/worktimeApi.js
```

После login frontend должен смотреть:

```js
user.role
user.scope
user.department
user.employee_id
```

И открывать нужный интерфейс:

| Role | Главный экран |
|---|---|
| `executive` | `ExecutiveDashboard` |
| `department_manager` | текущий `Dashboard` отдела |
| `hr` | `HRDashboard` |
| `employee` | `EmployeeCabinet` |

---

## 5.2. Добавить экран полного руководителя

Файл:

```text
frontend/src/pages/ExecutiveDashboard.jsx
```

Показывать:

- все отделы;
- общее количество сотрудников;
- средний риск по компании;
- отделы с высоким риском;
- топ сотрудников по риску;
- общее количество конфликтов;
- среднюю загрузку;
- сравнение отделов;
- переход к конкретному отделу.

---

## 5.3. Обновить интерфейс руководителя отдела

Текущий дашборд оставить как основу.

Добавить:

- кнопку “Создать задачу” в карточке сотрудника;
- кнопку “Запросить подтверждение графика”;
- блок “Статус подтверждения графиков”;
- список задач отдела;
- фильтр задач по статусу;
- отображение, кто подтвердил график, а кто нет.

---

## 5.4. Добавить HRDashboard

Файл:

```text
frontend/src/pages/HRDashboard.jsx
```

Показывать:

- все устаревшие графики;
- HR/data mismatches;
- timezone conflicts;
- сотрудники без подтверждения;
- отсутствия;
- data-quality;
- HR-задачи;
- возможность создать задачу сотруднику.

---

## 5.5. Добавить личный кабинет сотрудника

Файл:

```text
frontend/src/pages/EmployeeCabinet.jsx
```

Показывать:

| Блок | Что внутри |
|---|---|
| Мой график | дни, часы, формат, часовой пояс |
| Моя актуальность | дата обновления, актуальность, риск |
| Мои события | встречи и конфликты |
| Мои задачи | задачи от руководителя/HR |
| Действия | подтвердить график, запросить изменение, оставить комментарий |

Кнопки:

- “Подтвердить график”;
- “Запросить изменение”;
- “Принять задачу”;
- “Отклонить с комментарием”.

---

## 5.6. Добавить компоненты задач

Новые компоненты:

```text
frontend/src/components/TaskCard.jsx
frontend/src/components/TaskForm.jsx
frontend/src/components/TaskStatusBadge.jsx
frontend/src/components/RoleBadge.jsx
```

---

## 5.7. Обновить frontend API client

**Файл:** `frontend/src/api/worktimeApi.js`

Добавить функции:

```js
export async function loadTasks(user) {}
export async function loadMyTasks(user) {}
export async function createTask(payload) {}
export async function updateTaskStatus(taskId, payload) {}
export async function confirmSchedule(employeeId, payload) {}
export async function loadRiskExplanation(employeeId) {}
```

---

# 6. Остальные missing / ограничения проекта

## 6.1. Production-авторизация

Сейчас login demo-уровня. Нужно не говорить, что это production-auth.

| Сейчас | Нужно дальше |
|---|---|
| demo users в `users.json` | база пользователей |
| plain password | хеширование |
| demo-token | JWT/session |
| role как поле | RBAC/ABAC |

## 6.2. База данных

Сейчас CSV/JSON. Дальше: SQLite для MVP+ или PostgreSQL для production.

## 6.3. Реальные интеграции

Сейчас источники имитируются через synthetic data.

| Источник | Сейчас | Дальше |
|---|---|---|
| календарь | `events.csv` | Google Calendar / Outlook |
| HR | `hr_profiles.csv` | HRM |
| задачи | будущий `tasks.json` | Jira / YouTrack |
| табель | `absences.csv` | система учёта времени |
| уведомления | `/notifications` | email / Telegram / Slack |

## 6.4. История изменений

Нужно хранить:

- кто изменил график;
- когда;
- что было до/после;
- комментарий;
- кто подтвердил.

## 6.5. AI-ассистент

Сейчас есть объяснимые рекомендации и risk explanation, но нет отдельного AI-chat.

---

## 7. Что важно не сломать

| Уже есть | Не ломать |
|---|---|
| `/auth/login` | сохранить совместимость |
| `/api/worktime/overview?department=...` | оставить для руководителей отделов |
| текущие страницы frontend | не удалять |
| fallback на mock | оставить |
| `schedule_actuality` | не менять |
| поля employees/events/hr_profiles/absences | не переименовывать |
| data-quality | сохранить |
| backend tests | расширить, не удалить |

---

## 8. Критерии готовности следующего этапа

| Блок | Критерий |
|---|---|
| Роли | разные роли видят разные интерфейсы |
| Полный руководитель | видит все отделы и общую аналитику |
| Руководитель отдела | видит только свой отдел |
| HR | видит HR-проблемы всех отделов |
| Сотрудник | видит только себя и свои задачи |
| Задачи | руководитель/HR создаёт задачу, сотрудник отвечает |
| Подтверждение графика | сотрудник может подтвердить график |
| Риск | считается с весами отдела |
| Risk explanation | показывает веса и объяснение |
| Старый MVP | продолжает работать |
