# WorkTime Sync — тест-кейсы V2.9

Цель: проверить backend API, frontend UI, deploy и полный демонстрационный сценарий.

---

## 1. Smoke tests

| ID | Проверка | Ожидаемый результат |
|---|---|---|
| SM-01 | Открыть frontend | Экран входа WorkTime Sync v2.9 |
| SM-02 | `GET /api/health` | `{"status":"ok"}` |
| SM-03 | `GET /api/health/data` | counts по данным |
| SM-04 | Swagger `/docs` | открывается |
| SM-05 | Перезагрузка страницы frontend | SPA не падает |

---

## 2. Login и роли

| ID | Пользователь | Ожидаемый экран |
|---|---|---|
| AUTH-01 | `executive_demo / test0` | Executive dashboard |
| AUTH-02 | `hr_demo / testhr` | HR dashboard |
| AUTH-03 | `zarix / i9VUibm6` | Dashboard Core Platform |
| AUTH-04 | `gleb_employee / emp5` | Employee cabinet |
| AUTH-05 | неверный пароль | ошибка входа |

---

## 3. Scope-доступ

| ID | Проверка | Ожидаемый результат |
|---|---|---|
| SCOPE-01 | manager Core Platform видит сотрудников | только Core Platform |
| SCOPE-02 | manager не видит чужой отдел | доступ закрыт |
| SCOPE-03 | employee видит `/api/employees/me` | только свой профиль |
| SCOPE-04 | employee не может смотреть чужой профиль | 403 |
| SCOPE-05 | HR видит всех | доступ есть |
| SCOPE-06 | executive видит всех | доступ есть |

---

## 4. Задачи

| ID | Проверка | Ожидаемый результат |
|---|---|---|
| TASK-01 | manager создаёт `confirm_schedule` | задача создана |
| TASK-02 | manager создаёт задачу чужому отделу | 403 |
| TASK-03 | employee подтверждает задачу | status `confirmed` |
| TASK-04 | employee отклоняет без комментария | 400 |
| TASK-05 | employee отклоняет с комментарием | status `rejected` |
| TASK-06 | HR создаёт задачу любому сотруднику | задача создана |
| TASK-07 | executive создаёт задачу любому сотруднику | задача создана |

---

## 5. Задачи по встречам

| ID | Проверка | Ожидаемый результат |
|---|---|---|
| MT-01 | создать `meeting_confirmation` без `related_event_id` | 400 |
| MT-02 | создать meeting task с чужим event | 400 |
| MT-03 | создать `reschedule_meeting` без suggested time | 400 |
| MT-04 | создать `reschedule_meeting` с suggested time | задача создана |
| MT-05 | employee подтверждает перенос | status `confirmed` |
| MT-06 | employee предлагает другое время | status `reschedule_requested` |
| MT-07 | employee отказывается с комментарием | status `rejected` |
| MT-08 | manager применяет перенос | task `done`, event обновлён |
| MT-09 | employee пытается применить перенос | 403 |
| MT-10 | `meeting_outside_work_approval` + предложить перенос | status `reschedule_requested` |
| MT-11 | применить перенос для `meeting_outside_work_approval` | event обновлён |

---

## 6. Подтверждение графика

| ID | Проверка | Ожидаемый результат |
|---|---|---|
| SCH-01 | employee нажимает “Подтвердить график” | confirmation status `confirmed` |
| SCH-02 | pending `confirm_schedule` синхронизируется | задача становится `confirmed` |
| SCH-03 | reload после подтверждения | статус сохранён |
| SCH-04 | manager подтверждает график сотрудника своего отдела | разрешено |
| SCH-05 | manager подтверждает чужой отдел | 403 |

---

## 7. Автогенерация задач

| ID | Проверка | Ожидаемый результат |
|---|---|---|
| GEN-01 | manager генерирует задачи по конфликтам | создаются задачи в его scope |
| GEN-02 | повторная генерация | дубли не создаются |
| GEN-03 | employee пытается генерировать | 403 |
| GEN-04 | HR генерирует | работает по компании |
| GEN-05 | response показывает `created` | пользователь видит результат |

---

## 8. Availability

| ID | Проверка | Ожидаемый результат |
|---|---|---|
| AV-01 | открыть карту доступности | отображается сетка |
| AV-02 | ячейка показывает count | видно число доступных |
| AV-03 | tooltip показывает выпадающих | есть причины |
| AV-04 | лучший слот отображается | есть 2–3 предложения |
| AV-05 | детализация свободных сотрудников | если нет — доработка |

---

## 9. UX-проверки

| ID | Проверка | Ожидаемый результат |
|---|---|---|
| UX-01 | У meeting task понятные кнопки | не просто “Подтвердить” |
| UX-02 | У события видна дата | дата + день недели + время |
| UX-03 | datetime вводится удобно | `datetime-local`, не ручной ISO |
| UX-04 | employee видит активные/закрытые задачи | задачи разделены по смыслу |
| UX-05 | empty states | нет пустых экранов |
| UX-06 | notice после действия | сообщение понятно |

---

## 10. Deploy tests

| ID | Проверка | Ожидаемый результат |
|---|---|---|
| DEP-01 | открыть домен | frontend, не Not Found |
| DEP-02 | прямой URL `/tasks` | SPA открывается |
| DEP-03 | `POST /api/auth/login` | 200 |
| DEP-04 | `POST /api/tasks` | 200/201 |
| DEP-05 | `PATCH /api/tasks/{id}/status` | 200 |
| DEP-06 | `PATCH /api/employees/{id}/confirm-schedule` | 200 |
| DEP-07 | `POST /api/tasks/{id}/apply` | 200 |
| DEP-08 | reload после действия | данные сохранены |
| DEP-09 | backend после reboot | service active |
| DEP-10 | права записи data dir | save работает |

---

## 11. Основной сценарий демонстрации

1. Login: `zarix / i9VUibm6`.
2. Создать задачу по встрече.
3. Login: `gleb_employee / emp5`.
4. Открыть личный кабинет.
5. Ответить на задачу.
6. Login: `zarix / i9VUibm6`.
7. Применить решение.
8. Проверить, что задача закрыта.
9. Проверить, что событие обновлено.

---

## 12. Блокеры

| Блокер | Почему |
|---|---|
| сайт не открывается | нельзя показать MVP |
| login не работает | нельзя показать роли |
| кнопки дают 405 | ломается демонстрация |
| задачи не создаются | нет workflow |
| employee не видит задачи | нет пользовательского сценария |
| apply не работает | нет главной оригинальности |
| данные не сохраняются | после reload MVP выглядит сломанным |
