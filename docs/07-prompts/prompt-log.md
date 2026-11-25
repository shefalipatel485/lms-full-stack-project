# AI Prompt Log & Human Review Record

| Prompt ID | Date | Module / Phase | Goal | Issues Found & Human Review | Result |
|---|---|---|---|---|---|
| P-001 | 2026-11-25 | Database Schema | Generate 24 SQLAlchemy ORM models with constraints | Verified unique constraints on `(batch_id, student_id, session_date)` and `(student_id, course_id)` | Accepted |
| P-002 | 2026-11-25 | Auth & RBAC | Implement JWT login & `require_roles` dependency | Ensured inactive accounts return 403 and generic error on invalid login | Accepted |
| P-003 | 2026-11-25 | Quiz Engine | Build MCQ quiz creation & backend scoring | Stripped `is_correct` from student GET payload to prevent answer leakage | Accepted |
| P-004 | 2026-11-25 | Certificates | Generate downloadable PDF certificates | Added ReportLab landscape certificate with unique ID verification endpoint | Accepted |
| P-005 | 2026-11-25 | Frontend UI | Build responsive React + Tailwind dashboards | Connected all 15 screens to live FastAPI endpoints with role-aware sidebar | Accepted |
