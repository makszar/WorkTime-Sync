# Backend update package

Что входит:

```text
backend/app/main.py
backend/app/data_loader.py
backend/app/data_quality.py
backend/tests/test_api.py
backend/tests/test_data_loader.py
backend/tests/test_real_synthetic_data.py
data/synthetic/users.json
.github/workflows/backend-ci.yml
README.md
backend/README.md
```

После замены:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Проверить вручную:

```text
http://127.0.0.1:8040/health/data
http://127.0.0.1:8040/analytics/data-quality
http://127.0.0.1:8040/data/source
http://127.0.0.1:8040/schemas
http://127.0.0.1:8040/api/worktime/overview?department=Product%20UI
```
