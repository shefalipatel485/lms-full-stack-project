# EduSphere — Full Stack Learning Management System (LMS)

Complete role-based Learning Management System built with **React.js, Tailwind CSS, Python FastAPI, SQLAlchemy, MySQL, and JWT Authentication**, deployed on **Render** (backend) and **Vercel** (frontend) with **Aiven Cloud MySQL**.

## Live Deployment

| Service | Platform | Live URL |
|---|---|---|
| **Frontend App** | Vercel | https://lms-full-stack-project-rho.vercel.app |
| **Backend API** | Render | https://lms-full-stack-project-hjz6.onrender.com |
| **Swagger API Docs** | Render | https://lms-full-stack-project-hjz6.onrender.com/docs |
| **Database** | Aiven Cloud MySQL | Managed MySQL (`PyMySQL` over SSL/TLS) |

## Folder Structure
```text
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── middleware/
│   │   └── dependencies/
│   ├── migrations/
│   ├── tests/
│   ├── uploads/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── layouts/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── assets/
│   │   ├── context/
│   │   ├── routes/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── .env.example
├── docs/
│   ├── 01-requirements/
│   ├── 02-design/
│   ├── 03-business-rules/
│   ├── 04-architecture/
│   ├── 05-api/
│   ├── 06-modules/
│   ├── 07-prompts/
│   ├── 08-testing/
│   ├── 09-deployment/
│   ├── 10-user-manual/
│   └── 11-reports/
└── screenshots/
```

## Demo Login Credentials (Pre-seeded Automatically)
| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@lms.edu` | `Admin@123` |
| **Instructor** | `instructor@lms.edu` | `Instructor@123` |
| **Student** | `student@lms.edu` | `Student@123` |

## Deployment Configuration & Environment Variables

* **Render (Backend):** Configure `DATABASE_URL` (`mysql+pymysql://...`), `SECRET_KEY`, `ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `BACKEND_CORS_ORIGINS` (e.g., `https://lms-full-stack-project-rho.vercel.app`), and `PYTHON_VERSION=3.11.11` (never commit real secrets to Git).
* **Vercel (Frontend):** Set `VITE_API_BASE_URL=https://lms-full-stack-project-hjz6.onrender.com` and redeploy after updating environment variables.
* **Reports & Documentation:** Additional deployment and project report details are available under `docs/09-deployment/` and `docs/11-reports/`.

## Quick Start in VS Code

### 1. Run Backend (FastAPI)
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Optional: Set DATABASE_URL in .env to MySQL (e.g., mysql+pymysql://root:pass@localhost:3306/lms_db)
# If left unconfigured, it automatically uses local SQLite (lms_local.db) for instant testing!
uvicorn app.main:app --reload --port 8000
```
- Swagger API Docs: `http://localhost:8000/docs`

### 2. Run Automated Tests (Pytest)
```bash
cd backend
pytest -v
```

### 3. Run Frontend (React + Vite + Tailwind)
Open a second terminal in VS Code:
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
- Open App: `http://localhost:5173`
