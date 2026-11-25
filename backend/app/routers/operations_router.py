import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database import get_db
from app.models.lms_models import (
    Attendance, Batch, Payment, Certificate, Enrollment,
    Notification, Announcement, Course, User, Submission
)
from app.schemas.lms_schemas import AttendanceBulkCreate, PaymentCreate, AnnouncementCreate
from app.dependencies.auth_deps import get_current_user, require_roles
from app.services.certificate_service import generate_certificate_pdf

router = APIRouter(prefix="/api", tags=["Attendance, Payments, Certificates & Reports"])

# --- ATTENDANCE ---
@router.get("/attendance")
def get_attendance(batch_id: int = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Attendance)
    if current_user.role.name == "student":
        query = query.filter(Attendance.student_id == current_user.id)
    elif batch_id:
        query = query.filter(Attendance.batch_id == batch_id)

    records = query.order_by(Attendance.session_date.desc()).all()
    eligible = [r for r in records if r.status != "Holiday"]
    present = [r for r in eligible if r.status == "Present"]
    pct = round((len(present) / len(eligible)) * 100.0, 1) if eligible else 0.0

    return {
        "summary": {
            "total_eligible_classes": len(eligible),
            "present_classes": len(present),
            "attendance_percentage": pct
        },
        "records": [
            {
                "id": r.id,
                "batch_id": r.batch_id,
                "student_id": r.student_id,
                "session_date": r.session_date,
                "status": r.status,
                "remarks": r.remarks
            }
            for r in records
        ]
    }

@router.post("/attendance", status_code=201)
def mark_bulk_attendance(
    payload: AttendanceBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "instructor"]))
):
    batch = db.query(Batch).filter(Batch.id == payload.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    for item in payload.records:
        existing = db.query(Attendance).filter(
            Attendance.batch_id == payload.batch_id,
            Attendance.student_id == item.student_id,
            Attendance.session_date == payload.session_date
        ).first()
        if existing:
            existing.status = item.status
            existing.remarks = item.remarks
            existing.marked_by = current_user.id
        else:
            db.add(Attendance(
                batch_id=payload.batch_id,
                student_id=item.student_id,
                session_date=payload.session_date,
                status=item.status,
                remarks=item.remarks,
                marked_by=current_user.id
            ))
    db.commit()
    return {"message": f"Attendance saved for {len(payload.records)} students on {payload.session_date}"}

# --- PAYMENTS ---
@router.get("/payments")
def list_payments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Payment)
    if current_user.role.name == "student":
        query = query.filter(Payment.student_id == current_user.id)
    elif current_user.role.name == "instructor":
        raise HTTPException(status_code=403, detail="Instructors do not have access to fee records")

    payments = query.order_by(Payment.id.desc()).all()
    return [
        {
            "id": p.id,
            "receipt_number": p.receipt_number,
            "student_id": p.student_id,
            "student_name": p.student.full_name if p.student else "",
            "course_id": p.course_id,
            "course_title": p.course.title if p.course else "",
            "total_fee": p.total_fee,
            "amount_paid": p.amount_paid,
            "pending_amount": p.pending_amount,
            "payment_method": p.payment_method,
            "status": p.status,
            "notes": p.notes,
            "payment_date": p.payment_date
        }
        for p in payments
    ]

@router.post("/payments", status_code=201)
def record_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["admin"]))
):
    pending = max(0.0, payload.total_fee - payload.amount_paid)
    status_val = payload.status
    if pending == 0 and payload.amount_paid >= payload.total_fee:
        status_val = "Paid"
    elif 0 < payload.amount_paid < payload.total_fee:
        status_val = "Partially Paid"

    receipt = f"RCP-{date.today().year}-{uuid.uuid4().hex[:6].upper()}"
    pmt = Payment(
        receipt_number=receipt,
        student_id=payload.student_id,
        course_id=payload.course_id,
        total_fee=payload.total_fee,
        amount_paid=payload.amount_paid,
        pending_amount=pending,
        payment_method=payload.payment_method,
        status=status_val,
        notes=payload.notes
    )
    db.add(pmt)
    db.commit()
    db.refresh(pmt)
    return {"id": pmt.id, "receipt_number": pmt.receipt_number, "status": pmt.status, "pending_amount": pending}

# --- CERTIFICATES ---
@router.get("/certificates")
def list_certificates(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Certificate)
    if current_user.role.name == "student":
        query = query.filter(Certificate.student_id == current_user.id)
    certs = query.all()
    return [
        {
            "id": c.id,
            "certificate_number": c.certificate_number,
            "student_name": c.student.full_name if c.student else "",
            "course_id": c.course_id,
            "course_title": c.course.title if c.course else "",
            "issued_date": c.issued_date
        }
        for c in certs
    ]

@router.post("/certificates/generate/{course_id}", status_code=201)
def generate_student_certificate(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["student"]))
):
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()
    if not enrollment or enrollment.progress_percent < 100.0:
        raise HTTPException(status_code=400, detail="Course completion must be 100% before generating certificate")

    existing = db.query(Certificate).filter(
        Certificate.student_id == current_user.id,
        Certificate.course_id == course_id
    ).first()
    if existing:
        return {"certificate_number": existing.certificate_number, "message": "Certificate already issued"}

    cert_no = f"CERT-LMS-{date.today().year}-{uuid.uuid4().hex[:5].upper()}"
    cert = Certificate(certificate_number=cert_no, student_id=current_user.id, course_id=course_id)
    db.add(cert)
    db.commit()
    return {"certificate_number": cert_no, "message": "Certificate generated successfully"}

@router.get("/certificates/verify/{cert_number}")
def verify_certificate(cert_number: str, db: Session = Depends(get_db)):
    cert = db.query(Certificate).filter(Certificate.certificate_number == cert_number.strip()).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Invalid certificate number")
    return {
        "valid": True,
        "certificate_number": cert.certificate_number,
        "student_name": cert.student.full_name if cert.student else "",
        "course_title": cert.course.title if cert.course else "",
        "issued_date": cert.issued_date
    }

@router.get("/certificates/{cert_number}/download")
def download_certificate_pdf(cert_number: str, db: Session = Depends(get_db)):
    cert = db.query(Certificate).filter(Certificate.certificate_number == cert_number.strip()).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    pdf_bytes = generate_certificate_pdf(
        student_name=cert.student.full_name if cert.student else "Student",
        course_title=cert.course.title if cert.course else "Course",
        cert_number=cert.certificate_number,
        issued_date=str(cert.issued_date)
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={cert.certificate_number}.pdf"}
    )

# --- NOTIFICATIONS & ANNOUNCEMENTS ---
@router.get("/notifications")
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notifs = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.id.desc()).all()
    announcements = db.query(Announcement).order_by(Announcement.id.desc()).limit(10).all()
    return {
        "notifications": [
            {"id": n.id, "title": n.title, "message": n.message, "event_type": n.event_type, "is_read": n.is_read, "created_at": n.created_at}
            for n in notifs
        ],
        "announcements": [
            {"id": a.id, "title": a.title, "content": a.content, "target_role": a.target_role, "created_at": a.created_at}
            for a in announcements
        ]
    }

@router.post("/announcements", status_code=201)
def create_announcement(
    payload: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "instructor"]))
):
    ann = Announcement(**payload.model_dump(), created_by=current_user.id)
    db.add(ann)
    db.commit()
    return {"id": ann.id, "title": ann.title}

# --- DASHBOARD & ANALYTICS REPORTS ---
@router.get("/reports/dashboard")
def get_dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    role = current_user.role.name

    if role == "admin":
        total_students = db.query(User).filter(User.role.has(name="student")).count()
        total_instructors = db.query(User).filter(User.role.has(name="instructor")).count()
        total_courses = db.query(Course).count()
        active_batches = db.query(Batch).filter(Batch.status == "Active").count()
        total_revenue = db.query(func.coalesce(func.sum(Payment.amount_paid), 0.0)).scalar()
        pending_fees = db.query(func.coalesce(func.sum(Payment.pending_amount), 0.0)).scalar()
        pending_evaluations = db.query(Submission).filter(Submission.status.in_(["Submitted", "Late Submission"])).count()

        course_stats = []
        for c in db.query(Course).all():
            course_stats.append({
                "name": c.code,
                "students": len(c.enrollments),
                "fee": c.fee
            })

        return {
            "role": "admin",
            "kpis": {
                "total_students": total_students,
                "total_instructors": total_instructors,
                "total_courses": total_courses,
                "active_batches": active_batches,
                "total_revenue": float(total_revenue),
                "pending_fees": float(pending_fees),
                "pending_evaluations": pending_evaluations
            },
            "chart_data": course_stats
        }

    elif role == "instructor":
        assigned_courses = db.query(Course).filter(Course.instructor_id == current_user.id).all()
        assigned_batches = db.query(Batch).filter(Batch.instructor_id == current_user.id).all()
        total_students = sum(len(b.students) for b in assigned_batches)
        pending_evals = db.query(Submission).filter(Submission.status.in_(["Submitted", "Late Submission"])).count()

        return {
            "role": "instructor",
            "kpis": {
                "assigned_courses": len(assigned_courses),
                "assigned_batches": len(assigned_batches),
                "total_students": total_students,
                "pending_evaluations": pending_evals
            },
            "chart_data": [
                {"name": b.name, "students": len(b.students), "capacity": b.capacity}
                for b in assigned_batches
            ]
        }

    else:
        enrollments = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()
        att_records = db.query(Attendance).filter(Attendance.student_id == current_user.id, Attendance.status != "Holiday").all()
        present_cnt = len([a for a in att_records if a.status == "Present"])
        att_pct = round((present_cnt / len(att_records)) * 100.0, 1) if att_records else 100.0
        avg_progress = round(sum(e.progress_percent for e in enrollments) / len(enrollments), 1) if enrollments else 0.0

        return {
            "role": "student",
            "kpis": {
                "enrolled_courses": len(enrollments),
                "attendance_percentage": att_pct,
                "average_progress": avg_progress,
                "certificates_earned": db.query(Certificate).filter(Certificate.student_id == current_user.id).count()
            },
            "chart_data": [
                {"name": e.course.code if e.course else f"C-{e.course_id}", "progress": e.progress_percent}
                for e in enrollments
            ]
        }
