# Деплой WorkTime-Sync на порт 8040

## Что важно

- Backend FastAPI запускается на `127.0.0.1:8040`.
- Frontend в production ходит на `/api/...` и `/auth/...` через текущий домен.
- Для этого в `frontend/.env.production` оставлено `VITE_API_BASE_URL=`.

## Быстрая проверка backend

```bash
cd /var/www/worktimesync.ru/backend
source .venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8040
curl http://127.0.0.1:8040/health
```

## Сборка frontend

```bash
cd /var/www/worktimesync.ru/frontend
npm install
npm run build
```

## Nginx

Пример конфига лежит в `deploy/nginx-worktimesync.ru.conf`. В нём `/api`, `/auth` и `/health` проксируются на `http://127.0.0.1:8040`.

## Демо-аккаунты

| Логин | Пароль | Отдел |
|---|---|---|
| zarix | i9VUibm6 | Core Platform |
| lixxxa | test1 | Product UI |
| baftype | test2 | People Ops |
| ssdshkaaa | test3 | Delivery |
| agentemy | test4 | Quality |
