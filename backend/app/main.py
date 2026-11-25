import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.services.seed_service import seed_initial_data
from app.routers import (
    auth_router, users_router, courses_router,
    batches_router, lectures_router, assessments_router,
    operations_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version="1.1.0",
    description="Role-Based Learning Management System (Admin, Instructor, Student) REST API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(courses_router.router)
app.include_router(batches_router.router)
app.include_router(lectures_router.router)
app.include_router(assessments_router.router)
app.include_router(operations_router.router)

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.1.0"
    }
