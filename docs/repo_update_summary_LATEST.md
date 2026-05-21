# WorkTime-Sync - обновление под текущую структуру репозитория

## Что изменено

- `frontend/src/App.jsx` - добавлен экран логина, хранение текущего пользователя, загрузка данных с учётом отдела пользователя.
- `frontend/src/components/Layout.jsx` - боковой сайдбар заменён верхним хедером, убран знак WS и подпись под логотипом, оставлен текстовый логотип WorkTime-Sync.
- `frontend/src/components/EmployeeCard.jsx` - кнопка карточки получила SVG-иконку, карточки подготовлены к одинаковой высоте.
- `frontend/src/pages/Employees.jsx` - страница показывает отдел текущего руководителя и 5 закреплённых сотрудников.
- `frontend/src/pages/Dashboard.jsx` - обновлены подписи под демо на 25 синтетических сотрудников.
- `frontend/src/api/worktimeApi.js` - фронт сначала пробует FastAPI, при локальном запуске без бэка откатывается на mockData.
- `frontend/src/data/mockData.js` - добавлены 5 пользователей и 25 синтетических сотрудников по 5 отделам.
- `frontend/src/styles.css` - верхний хедер, экран логина, выравнивание карточек сотрудников, адаптив.
- `frontend/public/icons/*.svg` - добавлены переданные SVG-иконки для навигации и кнопок.
- `backend/app/main.py` - добавлен `/auth/login`, фильтрация данных по отделу через query-параметр `department`.
- `data/synthetic/users.json` - 5 профилей руководителей.
- `data/synthetic/employees.csv` - 25 сотрудников по 5 отделам.
- `data/synthetic/events.csv`, `data/synthetic/absences.csv`, `data/synthetic/hr_profiles.csv` - сценарии для кейса: устаревший график, перегруз, встречи вне рабочего времени, отсутствие, конфликт с HR-данными.

## Распределение аккаунтов

- `zarix / i9VUibm6` - Core Platform
- `lixxxa / test1` - Product UI
- `baftype / test2` - People Ops
- `ssdshkaaa / test3` - Delivery
- `agentemy / test4` - Quality

## Куда переносить

Содержимое архива нужно накатывать в корень репозитория `makszar/WorkTime-Sync` с заменой файлов.
