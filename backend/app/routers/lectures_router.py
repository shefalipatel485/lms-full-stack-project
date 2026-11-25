import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database import get_db
from app.models.lms_models import Lecture, StudyMaterial, LectureProgress, Enrollment, Course, User
from app.schemas.lms_schemas import LectureCreate, StudyMaterialCreate
from app.dependencies.auth_deps import get_current_user, require_roles
from app.config import settings

router = APIRouter(prefix="/api/lectures", tags=["Lectures & Materials"])

ALLOWED_EXTENSIONS = {".pdf", ".ppt", ".pptx", ".doc", ".docx", ".txt", ".mp4"}

@router.get("")
def list_lectures(course_id: int = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Lecture)
    if course_id:
        query = query.filter(Lecture.course_id == course_id)

    if current_user.role.name == "student":
        enrolled_cids = [e.course_id for e in db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()]
        query = query.filter(Lecture.course_id.in_(enrolled_cids))

    lectures = query.order_by(Lecture.sequence_order.asc()).all()
    completed_ids = {
        lp.lecture_id for lp in db.query(LectureProgress).filter(
            LectureProgress.student_id == current_user.id,
            LectureProgress.is_completed == True
        ).all()
    } if current_user.role.name == "student" else set()

    return [
        {
            "id": l.id,
            "course_id": l.course_id,
            "module_id": l.module_id,
            "title": l.title,
            "description": l.description,
            "video_url": l.video_url,
            "sequence_order": l.sequence_order,
            "duration_minutes": l.duration_minutes,
            "is_completed": l.id in completed_ids,
            "materials": [
                {"id": m.id, "title": m.title, "file_url": m.file_url, "file_type": m.file_type, "file_size_kb": m.file_size_kb}
                for m in l.materials
            ]
        }
        for l in lectures
    ]

@router.post("", status_code=201)
def create_lecture(
    payload: LectureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "instructor"]))
):
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role.name == "instructor" and course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this course")

    lec = Lecture(**payload.model_dump())
    db.add(lec)
    db.commit()
    db.refresh(lec)
    return {"id": lec.id, "title": lec.title}

@router.post("/materials", status_code=201)
def add_study_material_link(
    payload: StudyMaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "instructor"]))
):
    mat = StudyMaterial(
        lecture_id=payload.lecture_id,
        title=payload.title,
        file_url=payload.file_url,
        file_type=payload.file_type,
        file_size_kb=payload.file_size_kb,
        uploaded_by=current_user.id
    )
    db.add(mat)
    db.commit()
    db.refresh(mat)
    return {"id": mat.id, "title": mat.title}

@router.post("/upload-material", status_code=201)
async def upload_study_material_file(
    lecture_id: int = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "instructor"]))
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    content = await file.read()
    size_kb = max(1, len(content) // 1024)
    if size_kb > settings.MAX_UPLOAD_SIZE_MB * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_name)
    with open(file_path, "wb") as f:
        f.write(content)

    mat = StudyMaterial(
        lecture_id=lecture_id,
        title=title,
        file_url=f"/uploads/{safe_name}",
        file_type=ext.replace(".", "").upper(),
        file_size_kb=size_kb,
        uploaded_by=current_user.id
    )
    db.add(mat)
    db.commit()
    db.refresh(mat)
    return {"id": mat.id, "file_url": mat.file_url, "title": mat.title}

@router.post("/{lecture_id}/complete")
def mark_lecture_complete(
    lecture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["student"]))
):
    lec = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lec:
        raise HTTPException(status_code=404, detail="Lecture not found")

    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == lec.course_id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="You are not enrolled in this course")

    existing = db.query(LectureProgress).filter(
        LectureProgress.student_id == current_user.id,
        LectureProgress.lecture_id == lecture_id
    ).first()
    if not existing:
        db.add(LectureProgress(student_id=current_user.id, lecture_id=lecture_id, is_completed=True))
        db.flush()

    # Recalculate Course Progress %
    total_lectures = db.query(Lecture).filter(Lecture.course_id == lec.course_id).count()
    completed_lectures = db.query(LectureProgress).join(Lecture).filter(
        LectureProgress.student_id == current_user.id,
        Lecture.course_id == lec.course_id,
        LectureProgress.is_completed == True
    ).count()

    progress = round((completed_lectures / total_lectures) * 100.0, 1) if total_lectures > 0 else 0.0
    enrollment.progress_percent = progress
    if progress >= 100.0:
        enrollment.status = "Completed"
        enrollment.completed_at = func.now()

    db.commit()
    return {"message": "Lecture marked completed", "course_progress_percent": progress}
