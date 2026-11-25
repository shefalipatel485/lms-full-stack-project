from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.lms_models import (
    Role, User, Instructor, Course, CourseModule, Batch, BatchStudent,
    Enrollment, Lecture, StudyMaterial, LectureProgress, Assignment,
    Submission, AssignmentFeedback, Quiz, Question, QuizOption,
    QuizAttempt, Attendance, Payment, Notification, Announcement, Certificate
)
from app.utils.security import get_password_hash

def seed_initial_data(db: Session):
    # 1. Roles
    roles_data = [
        ("admin", "Institute Administrator with full system control"),
        ("instructor", "Faculty / Trainer managing assigned courses and batches"),
        ("student", "Enrolled learner accessing courses, quizzes, and assignments"),
    ]
    role_map = {}
    for r_name, r_desc in roles_data:
        role = db.query(Role).filter(Role.name == r_name).first()
        if not role:
            role = Role(name=r_name, description=r_desc)
            db.add(role)
            db.flush()
        role_map[r_name] = role

    if db.query(User).count() > 0:
        db.commit()
        return

    # 2. Users (Synthetic Demo Accounts)
    admin_user = User(
        full_name="Aarav Sharma (Admin)",
        email="admin@lms.edu",
        password_hash=get_password_hash("Admin@123"),
        phone="+91-9876500001",
        role_id=role_map["admin"].id,
        is_active=True
    )
    inst_1 = User(
        full_name="Prof. Neha Verma",
        email="instructor@lms.edu",
        password_hash=get_password_hash("Instructor@123"),
        phone="+91-9876500002",
        role_id=role_map["instructor"].id,
        is_active=True
    )
    inst_2 = User(
        full_name="Dr. Vikram Desai",
        email="vikram.instructor@lms.edu",
        password_hash=get_password_hash("Instructor@123"),
        phone="+91-9876500003",
        role_id=role_map["instructor"].id,
        is_active=True
    )
    stu_1 = User(
        full_name="Riya Patel",
        email="student@lms.edu",
        password_hash=get_password_hash("Student@123"),
        phone="+91-9876500004",
        role_id=role_map["student"].id,
        is_active=True
    )
    stu_2 = User(
        full_name="Kabir Mehta",
        email="kabir.student@lms.edu",
        password_hash=get_password_hash("Student@123"),
        phone="+91-9876500005",
        role_id=role_map["student"].id,
        is_active=True
    )
    db.add_all([admin_user, inst_1, inst_2, stu_1, stu_2])
    db.flush()

    db.add_all([
        Instructor(user_id=inst_1.id, expertise="Full Stack Web Development (React & FastAPI)", qualification="M.Tech CS", experience_years=8),
        Instructor(user_id=inst_2.id, expertise="Data Science, SQL & Cloud Architecture", qualification="Ph.D. Computer Science", experience_years=11),
    ])

    # 3. Courses
    c1 = Course(
        code="FSWD-101",
        title="Full Stack Web Development with React & FastAPI",
        description="Build modern production-grade web applications using React.js, Tailwind CSS, Python FastAPI, SQLAlchemy, and MySQL.",
        category="Software Engineering",
        duration_weeks=12,
        fee=24000.0,
        status="Published",
        instructor_id=inst_1.id
    )
    c2 = Course(
        code="DSML-202",
        title="Applied Data Analytics & SQL Mastery",
        description="Master relational database design, complex SQL queries, Python pandas, and business dashboard reporting.",
        category="Data Science",
        duration_weeks=8,
        fee=18000.0,
        status="Published",
        instructor_id=inst_2.id
    )
    db.add_all([c1, c2])
    db.flush()

    # 4. Modules
    m1 = CourseModule(course_id=c1.id, title="Module 1: Modern React & Tailwind Architecture", description="Hooks, Context API, Protected Routing, and SaaS UI design.", sequence_order=1)
    m2 = CourseModule(course_id=c1.id, title="Module 2: FastAPI, JWT & MySQL ORM", description="REST APIs, Pydantic schemas, SQLAlchemy models, and role permissions.", sequence_order=2)
    m3 = CourseModule(course_id=c2.id, title="Module 1: Relational Modeling & Normalization", description="ERD, primary/foreign keys, indexing, and transactions.", sequence_order=1)
    db.add_all([m1, m2, m3])
    db.flush()

    # 5. Batches
    b1 = Batch(
        name="FSWD-Nov2026-Morning",
        course_id=c1.id,
        instructor_id=inst_1.id,
        start_date=date.today() - timedelta(days=15),
        end_date=date.today() + timedelta(days=70),
        schedule_timing="Mon-Wed-Fri | 10:00 AM - 12:00 PM",
        capacity=25,
        status="Active"
    )
    b2 = Batch(
        name="DSML-Nov2026-Evening",
        course_id=c2.id,
        instructor_id=inst_2.id,
        start_date=date.today() - timedelta(days=10),
        end_date=date.today() + timedelta(days=45),
        schedule_timing="Tue-Thu-Sat | 06:00 PM - 08:00 PM",
        capacity=20,
        status="Active"
    )
    db.add_all([b1, b2])
    db.flush()

    # 6. Enrollments & Batch Students
    db.add_all([
        Enrollment(student_id=stu_1.id, course_id=c1.id, status="Active", progress_percent=50.0),
        Enrollment(student_id=stu_1.id, course_id=c2.id, status="Active", progress_percent=100.0, completed_at=datetime.now(timezone.utc)),
        Enrollment(student_id=stu_2.id, course_id=c1.id, status="Active", progress_percent=25.0),
        BatchStudent(batch_id=b1.id, student_id=stu_1.id),
        BatchStudent(batch_id=b1.id, student_id=stu_2.id),
        BatchStudent(batch_id=b2.id, student_id=stu_1.id),
    ])

    # 7. Lectures & Study Materials
    l1 = Lecture(
        course_id=c1.id, module_id=m1.id,
        title="1.1 Component Lifecycle, Hooks & State Management",
        description="Deep dive into useState, useEffect, custom hooks, and API integration patterns.",
        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        sequence_order=1, duration_minutes=45
    )
    l2 = Lecture(
        course_id=c1.id, module_id=m2.id,
        title="2.1 Designing Role-Based FastAPI Endpoints with JWT",
        description="Implementing OAuth2 password flow, bcrypt hashing, and RBAC dependencies.",
        video_url="https://www.youtube.com/watch?v=7t2alSnE2-I",
        sequence_order=2, duration_minutes=55
    )
    l3 = Lecture(
        course_id=c2.id, module_id=m3.id,
        title="1.1 Entity Relationship Diagrams & Constraints",
        description="Hands-on normalization up to 3NF with MySQL InnoDB.",
        video_url="https://www.youtube.com/watch?v=ztHopE5Wnpc",
        sequence_order=1, duration_minutes=50
    )
    db.add_all([l1, l2, l3])
    db.flush()

    db.add_all([
        StudyMaterial(lecture_id=l1.id, title="React_Hooks_CheatSheet.pdf", file_url="/docs/05-api/api-endpoints.md", file_type="PDF", file_size_kb=420, uploaded_by=inst_1.id),
        StudyMaterial(lecture_id=l2.id, title="FastAPI_JWT_Security_Guide.pdf", file_url="/docs/04-architecture/security.md", file_type="PDF", file_size_kb=510, uploaded_by=inst_1.id),
    ])

    db.add_all([
        LectureProgress(student_id=stu_1.id, lecture_id=l1.id, is_completed=True),
        LectureProgress(student_id=stu_1.id, lecture_id=l3.id, is_completed=True),
    ])

    # 8. Assignments & Submissions
    a1 = Assignment(
        course_id=c1.id, batch_id=b1.id,
        title="Build a Protected JWT Login & Dashboard UI",
        instructions="Create a responsive React login screen connected to FastAPI /api/auth/login and display role KPIs.",
        max_marks=100.0,
        due_date=datetime.now(timezone.utc) + timedelta(days=5),
        allow_late=True,
        created_by=inst_1.id
    )
    db.add(a1)
    db.flush()

    sub1 = Submission(
        assignment_id=a1.id, student_id=stu_1.id,
        submission_text="Completed JWT authentication flow with Axios interceptors and Tailwind KPI cards.",
        status="Evaluated", version=1
    )
    db.add(sub1)
    db.flush()

    db.add(AssignmentFeedback(
        submission_id=sub1.id, evaluator_id=inst_1.id,
        marks_obtained=92.0, comments="Clean component structure and accurate role validation."
    ))

    # 9. Quiz & Questions
    q1 = Quiz(
        course_id=c1.id, batch_id=b1.id,
        title="FastAPI & REST Security Assessment",
        description="Timed quiz covering HTTP status codes, JWT claims, and SQLAlchemy ORM.",
        total_marks=3.0, passing_marks=2.0, duration_minutes=10,
        allow_retake=True, created_by=inst_1.id
    )
    db.add(q1)
    db.flush()

    ques1 = Question(quiz_id=q1.id, question_text="Which HTTP status code indicates authenticated user lacks permission?", marks=1.0)
    ques2 = Question(quiz_id=q1.id, question_text="Which library is recommended in FastAPI for request/response validation?", marks=1.0)
    ques3 = Question(quiz_id=q1.id, question_text="Where should secret keys and database credentials be stored?", marks=1.0)
    db.add_all([ques1, ques2, ques3])
    db.flush()

    db.add_all([
        QuizOption(question_id=ques1.id, option_text="401 Unauthorized", is_correct=False),
        QuizOption(question_id=ques1.id, option_text="403 Forbidden", is_correct=True),
        QuizOption(question_id=ques1.id, option_text="404 Not Found", is_correct=False),
        QuizOption(question_id=ques2.id, option_text="Pydantic", is_correct=True),
        QuizOption(question_id=ques2.id, option_text="Jinja2", is_correct=False),
        QuizOption(question_id=ques2.id, option_text="Celery", is_correct=False),
        QuizOption(question_id=ques3.id, option_text="Hardcoded in React components", is_correct=False),
        QuizOption(question_id=ques3.id, option_text="Environment variables (.env excluded from Git)", is_correct=True),
        QuizOption(question_id=ques3.id, option_text="Public README.md", is_correct=False),
    ])

    # 10. Attendance
    for day_offset in range(1, 5):
        s_date = date.today() - timedelta(days=day_offset)
        db.add(Attendance(batch_id=b1.id, student_id=stu_1.id, session_date=s_date, status="Present", marked_by=inst_1.id))
        db.add(Attendance(batch_id=b1.id, student_id=stu_2.id, session_date=s_date, status="Present" if day_offset != 2 else "Absent", marked_by=inst_1.id))

    # 11. Payments
    db.add_all([
        Payment(
            receipt_number="RCP-2026-1001", student_id=stu_1.id, course_id=c1.id,
            total_fee=24000.0, amount_paid=15000.0, pending_amount=9000.0,
            payment_method="UPI", status="Partially Paid", notes="Installment 1 received"
        ),
        Payment(
            receipt_number="RCP-2026-1002", student_id=stu_1.id, course_id=c2.id,
            total_fee=18000.0, amount_paid=18000.0, pending_amount=0.0,
            payment_method="Bank Transfer", status="Paid", notes="Full course fee settled"
        ),
        Payment(
            receipt_number="RCP-2026-1003", student_id=stu_2.id, course_id=c1.id,
            total_fee=24000.0, amount_paid=24000.0, pending_amount=0.0,
            payment_method="Card", status="Paid", notes="Full payment"
        ),
    ])

    # 12. Certificate for completed course c2
    db.add(Certificate(
        certificate_number="CERT-LMS-2026-8841",
        student_id=stu_1.id,
        course_id=c2.id,
        issued_date=date.today()
    ))

    # 13. Notifications & Announcements
    db.add_all([
        Notification(user_id=stu_1.id, title="Assignment Evaluated", message="Your submission for 'Build a Protected JWT Login & Dashboard UI' scored 92/100.", event_type="Evaluation"),
        Notification(user_id=stu_1.id, title="Certificate Issued", message="Certificate CERT-LMS-2026-8841 is ready for Applied Data Analytics & SQL Mastery.", event_type="Certificate"),
        Notification(user_id=inst_1.id, title="New Batch Roster Updated", message="2 students are active in batch FSWD-Nov2026-Morning.", event_type="Batch"),
        Announcement(title="Welcome to Winter 2026 Academic Term", content="All live batch schedules and quiz windows are now active. Please check your dashboard.", target_role="All", created_by=admin_user.id),
    ])

    db.commit()
