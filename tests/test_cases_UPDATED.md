# Тест-кейсы WorkTime Sync

Тесты разделены на текущий backend V2.2, frontend-задачи и будущие задачи по встречам.

---

## 1. Backend V2.2

### TC-01. Healthcheck

| Поле | Значение |
|---|---|
| Endpoint | `GET /health` |
| Цель | проверить запуск backend |

Ожидаемый результат: `{"status": "ok"}`.

### TC-02. Health data

Endpoint: `GET /health/data`

Ожидаемый результат: в ответе есть employees, events, hr_profiles, absences, tasks, schedule_confirmations.

### TC-03. Login executive

`POST /auth/login`, логин `executive_demo`, пароль `test0`.

Ожидаемый результат: role = `executive`, scope = `all`, password не возвращается.

### TC-04. Login HR

`POST /auth/login`, логин `hr_demo`, пароль `testhr`.

Ожидаемый результат: role = `hr`, scope = `all`.

### TC-05. Login employee

`POST /auth/login`, логин `gleb_employee`, пароль `emp5`.

Ожидаемый результат: role = `employee`, scope = `self`, employee_id = 5.

### TC-06. Executive overview

Endpoint: `GET /api/worktime/overview?user_id=u0`.

Ожидаемый результат: видны все сотрудники, meta.role = `executive`, meta.scope = `all`.

### TC-07. Manager overview

Endpoint: `GET /api/worktime/overview?user_id=u1`.

Ожидаемый результат: видны только сотрудники Core Platform, tasks относятся только к отделу.

### TC-08. Employee overview

Endpoint: `GET /api/worktime/overview?user_id=emp5`.

Ожидаемый результат: виден только employee_id 5.

### TC-09. Employee cabinet

Endpoint: `GET /employees/me?user_id=emp5`.

Ожидаемый результат: возвращается карточка сотрудника, задачи и scheduleConfirmationStatus.

### TC-10. Tasks for manager

Endpoint: `GET /tasks?user_id=u1`.

Ожидаемый результат: руководитель видит задачи своего отдела и не видит задачи чужих отделов.

### TC-11. My tasks for employee

Endpoint: `GET /tasks/my?user_id=emp5`.

Ожидаемый результат: сотрудник видит только свои задачи.

### TC-12. Create task by manager

Endpoint: `POST /tasks?user_id=u1`.

Payload:

```json
{
  "employee_id": 5,
  "type": "confirm_schedule",
  "title": "Подтвердить график",
  "description": "Проверьте актуальность графика.",
  "due_date": "2026-05-24"
}
```

Ожидаемый результат: задача создана, status = `pending`, department = `Core Platform`.

### TC-13. Manager cannot assign outside department

Руководитель Core Platform пытается создать задачу сотруднику Product UI.

Ожидаемый результат: ошибка `403`.

### TC-14. Employee confirms task

Endpoint: `PATCH /tasks/{task_id}/status?user_id=emp5`.

Payload:

```json
{
  "status": "confirmed",
  "employee_comment": "Подтверждаю."
}
```

Ожидаемый результат: статус стал `confirmed`, комментарий сохранился.

### TC-15. Confirm schedule

Endpoint: `PATCH /employees/5/confirm-schedule?user_id=emp5`.

Ожидаемый результат: создаётся/обновляется confirmation, задача `confirm_schedule` становится `confirmed`, если была pending.

---

## 2. Тесты задач по встречам

### TC-16. Create meeting confirmation task

Создать задачу типа `meeting_confirmation` с `related_event_id`.

Ожидаемый результат: задача создана, `related_event_id` сохранён, событие существует.

### TC-17. Create reschedule meeting task

Создать задачу типа `reschedule_meeting`.

Ожидаемый результат: задача создана, сотрудник видит её в `/tasks/my`.

### TC-18. Invalid related_event_id

Создать задачу с несуществующим `related_event_id`.

Ожидаемый результат: backend возвращает `400`.

### TC-19. Task-event mismatch

Создать задачу сотруднику 5, но указать event другого сотрудника.

Ожидаемый результат: backend возвращает `400`.

### TC-20. Outside-work approval validation

Создать `meeting_outside_work_approval` для события, которое не выходит за рабочий график.

Ожидаемый результат: backend возвращает warning или `400`, в зависимости от выбранной логики.

---

## 3. Frontend tests

### TC-21. Role-based routing

| User | Expected page |
|---|---|
| executive_demo | ExecutiveDashboard |
| hr_demo | HRDashboard |
| zarix | Dashboard отдела |
| gleb_employee | EmployeeCabinet |

### TC-22. Employee sees task

Войти как `gleb_employee`, открыть личный кабинет.

Ожидаемый результат: видна задача `confirm_schedule`, есть кнопки подтвердить/отклонить.

### TC-23. Manager creates meeting task

Войти как `zarix`, открыть сотрудника Глеба, создать задачу по встрече.

Ожидаемый результат: задача появилась у сотрудника.

### TC-24. HR dashboard

Войти как `hr_demo`, открыть HRDashboard.

Ожидаемый результат: видны HR-расхождения, сотрудники без подтверждения и HR-задачи.

### TC-25. Executive dashboard

Войти как `executive_demo`, открыть ExecutiveDashboard.

Ожидаемый результат: видны все отделы, сравнение отделов, задачи и риски по компании.
