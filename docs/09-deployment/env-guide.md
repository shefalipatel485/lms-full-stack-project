# Environment & Configuration Guide
Copy `backend/.env.example` to `backend/.env` and `frontend/.env.example` to `frontend/.env`.
- `DATABASE_URL`: Set to `mysql+pymysql://USER:PASS@HOST:3306/lms_db` for MySQL (defaults to local SQLite if omitted so you can test immediately).
- `SECRET_KEY`: Use a 32+ character random secret string.
- `VITE_API_BASE_URL`: Backend URL (e.g., `http://localhost:8000` locally or Render URL in production).
