# Что отсутствует или требует уточнения по текущему состоянию WorkTime Sync

Документ фиксирует, что уже реализовано в MVP, а что остаётся ограничением или следующим шагом развития.

---

## Краткая сводка текущего состояния

| Область | Статус |
|---|---|
| Frontend | реализован на React + Vite |
| Backend | реализован на FastAPI |
| Основные данные | `data/synthetic/*.csv` |
| Demo-login | реализован |
| Фильтрация по department | реализована |
| Метрики | реализованы |
| Конфликты | реализованы |
| Карта доступности | реализована |
| Рекомендации | реализованы |
| Уведомления | реализованы как backend endpoint |
| Data-quality | реализован backend endpoint |
| Backend CI | реализован через GitHub Actions |
| Production-БД | не реализована |
| Реальные интеграции | не реализованы |
| Production-авторизация | не реализована |

---

## Уже реализовано

### Frontend

| Функция | Статус | Комментарий |
|---|---|---|
| экран входа | есть | demo-login руководителя отдела |
| дашборд | есть | показывает состояние department |
| список сотрудников | есть | после входа показывает сотрудников отдела |
| карточка сотрудника | есть | профиль, метрики, конфликты, рекомендации |
| конфликты | есть | события вне рабочего времени |
| доступность | есть | карта доступности и лучшие слоты |
| рекомендации | есть | действия для HR/PM/руководителя |
| fallback на mock-данные | есть | frontend может работать без backend |
| отдельный экран data-quality | нет | пока доступно через backend API |
| отдельный экран notifications | нет | пока доступно через backend API |
| отдельный экран groups | нет | пока доступно через backend API |
| отдельный экран risk explanation | нет | пока доступно через backend API |

### Backend

| Функция | Статус |
|---|---|
| FastAPI backend | есть |
| `POST /auth/login` | есть |
| `GET /health` | есть |
| `GET /health/data` | есть |
| `GET /data/source` | есть |
| `GET /schemas` | есть |
| `GET /api/worktime/overview` | есть |
| `GET /employees` | есть |
| `GET /employees/frontend` | есть |
| `GET /employees/{employee_id}` | есть |
| `GET /employees/{employee_id}/risk-explanation` | есть |
| `GET /analytics/summary` | есть |
| `GET /analytics/conflicts` | есть |
| `GET /analytics/data-mismatches` | есть |
| `GET /analytics/data-quality` | есть |
| `GET /analytics/availability` | есть |
| `GET /analytics/groups` | есть |
| `GET /recommendations` | есть |
| `GET /notifications` | есть |
| `GET /meeting-slots` | есть |
| `POST /upload/{dataset}` | есть |
| department-фильтр | есть |
| Pydantic-валидация | есть |
| backend CI | есть |

### Data

| Dataset | Статус | Количество |
|---|---|---:|
| `employees.csv` | есть | 25 |
| `events.csv` | есть | 60 |
| `hr_profiles.csv` | есть | 25 |
| `absences.csv` | есть | 3 |
| `users.json` | есть | 5 |

---

## Что требует уточнения или доработки

### 1. Production-авторизация

| Сейчас | Нужно для production |
|---|---|
| demo-пользователи в `users.json` | база пользователей |
| пароль хранится в synthetic file | хеширование паролей |
| demo-token | JWT/session token |
| фильтр department | полноценные права доступа |
| role как поле | RBAC/ABAC-модель |

### 2. База данных

| Сейчас | Нужно дальше |
|---|---|
| `employees.csv` | таблица employees |
| `events.csv` | таблица events |
| `hr_profiles.csv` | таблица HR profiles |
| `absences.csv` | таблица absences |
| `users.json` | таблица users |
| перечитывание файлов | запросы к БД |

### 3. Реальные интеграции

| Источник | Сейчас | Следующий шаг |
|---|---|---|
| календарь | `events.csv` | Google Calendar / Outlook |
| HR | `hr_profiles.csv` | HRM-система |
| задачи | часть событий в `events.csv` | Jira / YouTrack |
| табель | отсутствия в `absences.csv` | система учёта времени |
| уведомления | `/notifications` | email / Telegram / Slack |

### 4. Frontend не показывает все backend-возможности

| Backend-возможность | Где есть | Что добавить во frontend |
|---|---|---|
| groups | `/analytics/groups` | экран “Группы сотрудников” |
| notifications | `/notifications` | экран “Уведомления” |
| risk explanation | `/employees/{id}/risk-explanation` | блок “Почему такой риск” |
| data-quality | `/analytics/data-quality` | экран “Качество данных” |
| data source | `/data/source` | технический блок администратора |
| schemas | `/schemas` | подсказка для загрузки CSV |

### 5. UI для загрузки данных

Backend endpoint уже есть: `POST /upload/{dataset}`. Для пользователя нужен удобный экран загрузки employees/events/hr_profiles/absences с результатом валидации.

### 6. Реальные уведомления

| Сейчас | Следующий шаг |
|---|---|
| `GET /notifications` | email |
| уведомления в API | Telegram bot |
| recipientRole | Slack / Teams |
| action | push-уведомления в интерфейсе |

### 7. История изменений

Пока нет истории изменений графиков. Нужно хранить employee_id, changed_by, changed_at, old_value, new_value и reason.

### 8. AI-ассистент

Сейчас есть explainable recommendations и risk explanation, но нет отдельного AI-chat. Возможное развитие: вопросы “кто доступен завтра в 11?”, “почему высокий риск?”, “кого HR проверить первым?”.

---

## Что важно не обещать как уже готовое

| Не говорить | Лучше говорить |
|---|---|
| “У нас есть полноценная авторизация” | “Есть demo-login и department-фильтрация для MVP” |
| “Мы подключили Google Calendar” | “Календарь имитируется через synthetic events, архитектура готова к интеграции” |
| “У нас production-база данных” | “Сейчас CSV/JSON, следующий шаг — БД” |
| “Уведомления реально отправляются” | “Backend формирует уведомления, отправка — следующий этап” |
| “AI-ассистент реализован” | “Есть explainable risk и рекомендации; AI-ассистент — развитие” |

---

## Приоритет доработок после MVP

| Приоритет | Доработка | Почему важно |
|---:|---|---|
| 1 | экран “Почему такой риск” | усиливает объяснимость |
| 2 | экран “Качество данных” | показывает зрелость работы с данными |
| 3 | экран “Уведомления” | закрывает пункт кейса про уведомления |
| 4 | UI загрузки CSV/JSON | делает систему управляемой без Swagger |
| 5 | SQLite/PostgreSQL | переход от MVP к продукту |
| 6 | реальные интеграции | замена synthetic data |
| 7 | JWT/роли | production-доступ |
| 8 | AI-chat | интеллектуальный слой поверх метрик |
