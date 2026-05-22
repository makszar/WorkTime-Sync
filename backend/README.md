# WorkTime Sync Backend

Текущая версия backend: **1.4.0**.

## Главное

Backend теперь закрывает не только базовый API, но и слой проверки данных:

- основной источник данных: `data/synthetic/`;
- fallback: `backend/data/`;
- demo-login: `POST /auth/login`;
- фильтрация по отделу: `?department=Product`;
- диагностика данных: `/health/data`, `/data/source`, `/schemas`, `/analytics/data-quality`;
- безопасный upload: старый рабочий файл не удаляется, если новый файл не прошёл валидацию;
- GitHub Actions workflow для backend-тестов: `.github/workflows/backend-ci.yml`.

## Endpoint'ы

```text
POST /auth/login
GET /
GET /health
GET /health/data
GET /data/source
GET /schemas
GET /api/worktime/overview
GET /employees
GET /employees/frontend
GET /employees/{employee_id}
GET /employees/{employee_id}/risk-explanation
GET /analytics/summary
GET /analytics/conflicts
GET /analytics/data-mismatches
GET /analytics/data-quality
GET /analytics/availability
GET /analytics/groups
GET /recommendations
GET /notifications
GET /meeting-slots
POST /upload/{dataset}
```

## Фильтр отдела

Большинство аналитических endpoint'ов поддерживают query-параметр:

```text
?department=Core%20Platform
?department=Product%20UI
?department=People%20Ops
?department=Delivery
?department=Quality
```

Примеры:

```text
GET /api/worktime/overview?department=Product%20UI
GET /employees?department=Quality
GET /notifications?department=People%20Ops
GET /meeting-slots?department=Product%20UI
```

## Demo-login

Пользователи лежат в:

```text
data/synthetic/users.json
```

Актуальные профили:

```text
zarix / i9VUibm6 -> Core Platform
lixxxa / test1 -> Product UI
baftype / test2 -> People Ops
ssdshkaaa / test3 -> Delivery
agentemy / test4 -> Quality
```

`POST /auth/login` возвращает demo-token и пользователя без пароля.


## Данные

Главный источник данных:

```text
data/synthetic/
```

Backend ожидает:

```text
data/synthetic/employees.csv
data/synthetic/events.csv
data/synthetic/hr_profiles.csv
data/synthetic/absences.csv
data/synthetic/users.json
```

Также поддерживаются JSON-файлы с такими же dataset-name. Если CSV и JSON есть одновременно, CSV имеет приоритет.

Loader поддерживает текущий формат synthetic CSV:

```text
emp001 -> 1
evt001 -> 1
abs001 -> 1
Mon|Tue|Wed|Thu|Fri -> ["Mon", "Tue", "Wed", "Thu", "Fri"]
2026-05-20T10:00:00+03:00 -> 2026-05-20T10:00:00
```

## Диагностика данных

### `GET /health/data`

Проверяет, что backend реально загрузил данные.

### `GET /data/source`

Показывает, какие файлы реально используются.

### `GET /schemas`

Показывает ожидаемые колонки CSV/JSON.

### `GET /analytics/data-quality`

Проверяет:

- orphan events;
- orphan absences;
- HR-профили без сотрудников;
- сотрудники без HR-профиля;
- дубликаты id;
- некорректные интервалы событий;
- некорректные интервалы отсутствий.

## Upload

```text
POST /upload/{dataset}
```

Поддерживаемые dataset:

```text
employees
events
hr_profiles
absences
```

Upload безопасный:

1. файл сохраняется во временный путь;
2. валидируется;
3. только после успешной проверки заменяет старый файл;
4. если файл невалидный, старый рабочий файл остаётся на месте.

## Запуск

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8040 --reload
```

Swagger:

```text
http://127.0.0.1:8040/docs
```

## Тесты

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

Тесты проверяют API, login, department-фильтр, loader, data-quality, безопасный upload и реальные файлы `data/synthetic`.
