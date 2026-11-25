from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.lms_models import Course, CourseModule, Enrollment, User
from app.schemas.lms_schemas import CourseCreate, CourseUpdate, ModuleCreate
from app.dependencies.auth_deps import get_current_user, require_roles

router = APIRouter(prefix="/api/courses", tags=["Courses & Modules"])

@router.get("")
def list_courses(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Course)
    role = current_user.role.name

    if role == "instructor":
        query = query.filter(Course.instructor_id == current_user.id)
    elif role == "student":
        enrolled_ids = [e.course_id for e in db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()]
        query = query.filter((Course.id.in_(enrolled_ids)) | (Course.status == "Published"))

    if search:
        term = f"%{search.strip()}%"
        query = query.filter((Course.title.ilike(term)) | (Course.code.ilike(term)))
    if category:
        query = query.filter(Course.category.ilike(f"%{category.strip()}%"))
    if status:
        query = query.filter(Course.status == status)

    courses = query.order_by(Course.id.desc()).all()
    enrolled_map = {
        e.course_id: e for e in db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()
    } if role == "student" else {}

    result = []
    for c in courses:
        enr = enrolled_map.get(c.id)
        result.append({
            "id": c.id,
            "code": c.code,
            "title": c.title,
            "description": c.description,
            "category": c.category,
            "duration_weeks": c.duration_weeks,
            "fee": c.fee,
            "status": c.status,
            "instructor_id": c.instructor_id,
            "instructor_name": c.instructor.full_name if c.instructor else "Unassigned",
            "modules_count": len(c.modules),
            "enrolled_students_count": len(c.enrollments),
            "is_enrolled": enr is not None,
            "progress_percent": enr.progress_percent if enr else 0.0
        })
    return result

@router.get("/{course_id}")
def get_course_detail(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    modules = []
    for m in course.modules:
        modules.append({
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "sequence_order": m.sequence_order,
            "lectures": [
                {
                    "id": lec.id,
                    "title": lec.title,
                    "description": lec.description,
                    "video_url": lec.video_url,
                    "duration_minutes": lec.duration_minutes,
                    "sequence_order": lec.sequence_order,
                    "materials": [
                        {"id": mat.id, "title": mat.title, "file_url": mat.file_url, "file_type": mat.file_type}
                        for mat in lec.materials
                    ]
                }
                for lec in m.lectures
            ]
        })

    return {
        "id": course.id,
        "code": course.code,
        "title": course.title,
        "description": course.description,
        "category": course.category,
        "duration_weeks": course.duration_weeks,
        "fee": course.fee,
        "status": course.status,
        "instructor_id": course.instructor_id,
        "instructor_name": course.instructor.full_name if course.instructor else "Unassigned",
        "modules": modules
    }

@router.post("", status_code=201)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["admin"]))
):
    if db.query(Course).filter(Course.code == payload.code.strip().upper()).first():
        raise HTTPException(status_code=409, detail="Course code already exists")
    course = Course(
        code=payload.code.strip().upper(),
        title=payload.title,
        description=payload.description,
        category=payload.category,
        duration_weeks=payload.duration_weeks,
        fee=payload.fee,
        thumbnail_url=payload.thumbnail_url,
        status=payload.status,
        instructor_id=payload.instructor_id
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return {"id": course.id, "code": course.code, "title": course.title, "status": course.status}

@router.put("/{course_id}")
def update_course(
    course_id: int,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "instructor"]))
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role.name == "instructor" and course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Instructors can only edit their assigned courses")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    db.commit()
    return {"message": "Course updated", "id": course.id}

@router.delete("/{course_id}")
def delete_or_archive_course(
    course_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["admin"]))
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if len(course.enrollments) > 0 or len(course.batches) > 0:
        course.status = "Archived"
        db.commit()
        return {"message": "Course has active enrollments/batches; archived instead of hard delete."}
    db.delete(course)
    db.commit()
    return {"message": "Course deleted permanently"}

@router.post("/{course_id}/modules", status_code=201)
def add_course_module(
    course_id: int,
    payload: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "instructor"]))
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role.name == "instructor" and course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this course")

    mod = CourseModule(
        course_id=course_id,
        title=payload.title,
        description=payload.description,
        sequence_order=payload.sequence_order
    )
    db.add(mod)
    db.commit()
    db.refresh(mod)
    return {"id": mod.id, "title": mod.title}
