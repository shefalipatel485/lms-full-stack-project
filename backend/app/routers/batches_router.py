from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.lms_models import Batch, BatchStudent, Enrollment, User, Course
from app.schemas.lms_schemas import BatchCreate, BatchEnrollStudent
from app.dependencies.auth_deps import get_current_user, require_roles

router = APIRouter(prefix="/api/batches", tags=["Batches"])

@router.get("")
def list_batches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    role = current_user.role.name
    query = db.query(Batch)
    if role == "instructor":
        query = query.filter(Batch.instructor_id == current_user.id)
    elif role == "student":
        b_ids = [bs.batch_id for bs in db.query(BatchStudent).filter(BatchStudent.student_id == current_user.id).all()]
        query = query.filter(Batch.id.in_(b_ids))

    batches = query.order_by(Batch.id.desc()).all()
    return [
        {
            "id": b.id,
            "name": b.name,
            "course_id": b.course_id,
            "course_title": b.course.title if b.course else "",
            "instructor_id": b.instructor_id,
            "instructor_name": b.instructor.full_name if b.instructor else "Unassigned",
            "start_date": b.start_date,
            "end_date": b.end_date,
            "schedule_timing": b.schedule_timing,
            "capacity": b.capacity,
            "enrolled_count": len(b.students),
            "status": b.status,
            "roster": [
                {"id": bs.student.id, "full_name": bs.student.full_name, "email": bs.student.email}
                for bs in b.students if bs.student
            ]
        }
        for b in batches
    ]

@router.post("", status_code=201)
def create_batch(
    payload: BatchCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["admin"]))
):
    if db.query(Batch).filter(Batch.name == payload.name.strip()).first():
        raise HTTPException(status_code=409, detail="Batch name already exists")
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Linked course not found")

    batch = Batch(**payload.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return {"id": batch.id, "name": batch.name}

@router.post("/{batch_id}/enroll", status_code=201)
def enroll_student_in_batch(
    batch_id: int,
    payload: BatchEnrollStudent,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["admin"]))
):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    if len(batch.students) >= batch.capacity:
        raise HTTPException(status_code=400, detail="Batch capacity reached")

    student = db.query(User).filter(User.id == payload.student_id).first()
    if not student or student.role.name != "student":
        raise HTTPException(status_code=400, detail="Valid student account required")

    if db.query(BatchStudent).filter(BatchStudent.batch_id == batch_id, BatchStudent.student_id == payload.student_id).first():
        raise HTTPException(status_code=409, detail="Student is already enrolled in this batch")

    db.add(BatchStudent(batch_id=batch_id, student_id=payload.student_id))

    # Also ensure course enrollment exists
    existing_enr = db.query(Enrollment).filter(
        Enrollment.student_id == payload.student_id,
        Enrollment.course_id == batch.course_id
    ).first()
    if not existing_enr:
        db.add(Enrollment(student_id=payload.student_id, course_id=batch.course_id, status="Active"))

    db.commit()
    return {"message": f"{student.full_name} added to {batch.name}"}
