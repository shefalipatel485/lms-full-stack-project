# Database Migrations (Alembic)

Initialize or run migrations against MySQL:
```bash
alembic revision --autogenerate -m "initial_lms_schema"
alembic upgrade head
```
Note: `app/main.py` also runs `Base.metadata.create_all(bind=engine)` and automatic synthetic data seeding on startup for immediate local verification.
