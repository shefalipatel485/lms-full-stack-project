# Deployment Guide (Vercel + Render + Managed MySQL)
1. **Database:** Create a MySQL 8.0 database on Railway / Aiven / AWS RDS and run `backend/migrations/schema.sql`.
2. **Backend (Render):** Deploy `backend/` as a Python Web Service with start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Add `DATABASE_URL`, `SECRET_KEY`, and `BACKEND_CORS_ORIGINS`.
3. **Frontend (Vercel):** Deploy `frontend/` with build command `npm run build` and output directory `dist`. Set `VITE_API_BASE_URL` to your Render backend URL.
