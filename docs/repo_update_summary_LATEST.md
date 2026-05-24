# Сводка текущего состояния WorkTime Sync

## Что изменилось

Репозиторий обновлён до backend V2.2.

Backend уже реализовал:

- роли `executive`, `hr`, `department_manager`, `employee`;
- scope-доступ `all`, `department`, `self`;
- `tasks.json`;
- `schedule_confirmations.json`;
- task API;
- подтверждение графика;
- `/employees/me`;
- `/analytics/company`;
- `/analytics/hr-dashboard`;
- риск с весами отделов;
- расширенный risk explanation.

---

## Что пока не сделано

Главный gap — frontend.

Сейчас frontend всё ещё работает как старый MVP:

- login;
- dashboard;
- employees;
- profile;
- conflicts;
- availability;
- recommendations.

Не хватает:

- role-based UI;
- executive dashboard;
- HR dashboard;
- employee cabinet;
- task UI;
- create task UI;
- meeting task UI;
- confirm schedule UI;
- frontend API через `user_id`.

---

## Что нужно сделать с данными

Нужно добавить:

- employee-аккаунты для большего числа сотрудников;
- больше задач;
- разные статусы задач;
- задачи по встречам;
- больше подтверждений графика;
- `related_event_id` для задач по встречам.

---

## Самый важный следующий шаг

1. Расширить synthetic data.
2. Доработать backend для задач по встречам.
3. Подключить frontend к backend V2.2.
4. Сделать личный кабинет сотрудника.
5. Сделать UI задач для руководителя/HR/сотрудника.

---

## Как объяснять команде

Backend-команда:

> Backend V2.2 уже реализовал роли и задачи. Теперь нужно добавить задачи по встречам: новые task types, `related_event_id`, валидацию событий, расширение data-quality и тесты.

Frontend-команда:

> Нужно перестроить интерфейс под роли и подключить новые endpoint’ы: `/employees/me`, `/tasks`, `/tasks/my`, `/analytics/company`, `/analytics/hr-dashboard`, `/confirm-schedule`.

Data-команда:

> Нужно расширить `users.json`, `tasks.json`, `schedule_confirmations.json`, добавить сценарии задач по встречам и разные статусы.
