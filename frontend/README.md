# WorkTime Sync - frontend MVP

Это frontend-часть для кейса 3 хакатона Весенний код. Проект показывает дашборд актуальности рабочего времени, сотрудников, карточку сотрудника, конфликты, командную доступность и рекомендации.

## Что внутри

- React + Vite - основа интерфейса.
- CSS - внешний вид, адаптивность, карточки, таблицы и статусы.
- JavaScript - расчеты показателей, риска, актуальности, конфликтов и доступности.
- Моковые данные - команда из 25 синтетических сотрудников и 5 руководителей, события календаря и дорожная карта.
- API-слой - файл src/api/worktimeApi.js, куда можно подключить backend FastAPI.

## Как запустить

```bash
npm install
npm run dev
```

После запуска открыть адрес, который покажет Vite. Обычно это http://localhost:5173.

## Как подключить backend

1. Создать файл `.env` в корне проекта.
2. Добавить:

```bash
VITE_USE_MOCK_DATA=false
VITE_API_BASE_URL=http://127.0.0.1:8040
```

3. Backend должен отдавать `/api/worktime/overview` в формате:

```json
{
  "employees": [],
  "events": [],
  "roadmap": [],
  "summary": {},
  "recommendations": [],
  "bestSlots": []
}
```

## Главные файлы

- src/App.jsx - переключение экранов и загрузка данных.
- src/pages - страницы продукта.
- src/components - переиспользуемые UI-блоки.
- src/utils/calculations.js - формулы и аналитика.
- src/data/mockData.js - демонстрационные данные.
- src/styles.css - дизайн и адаптивность.

## Frontend v2.5

Версия v2.5 перестраивает интерфейс под роли `executive`, `hr`, `department_manager` и `employee`. Подключены страницы компании, HR-панель, кабинет сотрудника, задачи, подтверждение графика и endpoints `/employees/me`, `/tasks`, `/tasks/my`, `/analytics/company`, `/analytics/hr-dashboard`, `/confirm-schedule`.

