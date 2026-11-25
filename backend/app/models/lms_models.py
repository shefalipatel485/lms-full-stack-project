from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, Date,
    ForeignKey, UniqueConstraint, Index, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# 1. roles
class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # admin, instructor, student
    description = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="role")

# 2. users
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    role = relationship("Role", back_populates="users")
    instructor_profile = relationship("Instructor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    batch_links = relationship("BatchStudent", back_populates="student", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

# 7. instructors
class Instructor(Base):
    __tablename__ = "instructors"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    expertise = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)
    qualification = Column(String(150), nullable=True)
    experience_years = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="instructor_profile")

# 3. courses
class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, index=True, nullable=False)
    title = Column(String(180), index=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(80), index=True, nullable=False)
    duration_weeks = Column(Integer, nullable=False, default=8)
    fee = Column(Float, nullable=False, default=0.0)
    thumbnail_url = Column(String(255), nullable=True)
    status = Column(String(30), default="Published", index=True)  # Draft, Published, Archived
    instructor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    instructor = relationship("User", foreign_keys=[instructor_id])
    modules = relationship("CourseModule", back_populates="course", cascade="all, delete-orphan", order_by="CourseModule.sequence_order")
    batches = relationship("Batch", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")

# 4. course_modules
class CourseModule(Base):
    __tablename__ = "course_modules"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(180), nullable=False)
    description = Column(Text, nullable=True)
    sequence_order = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course", back_populates="modules")
    lectures = relationship("Lecture", back_populates="module", cascade="all, delete-orphan", order_by="Lecture.sequence_order")

# 5. batches
class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False)
    instructor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    schedule_timing = Column(String(120), nullable=False)  # e.g., "Mon-Wed-Fri 10:00 AM - 12:00 PM"
    capacity = Column(Integer, default=30, nullable=False)
    status = Column(String(30), default="Active", index=True)  # Upcoming, Active, Closed, Archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="batches")
    instructor = relationship("User", foreign_keys=[instructor_id])
    students = relationship("BatchStudent", back_populates="batch", cascade="all, delete-orphan")

# 6. batch_students
class BatchStudent(Base):
    __tablename__ = "batch_students"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("batch_id", "student_id", name="uq_batch_student"),)

    batch = relationship("Batch", back_populates="students")
    student = relationship("User", back_populates="batch_links")

# 10. enrollments
class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String(30), default="Active")  # Active, Completed, Dropped
    progress_percent = Column(Float, default=0.0)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uq_student_course_enrollment"),)

    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

# 8. lectures
class Lecture(Base):
    __tablename__ = "lectures"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(Integer, ForeignKey("course_modules.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(180), nullable=False)
    description = Column(Text, nullable=True)
    video_url = Column(String(500), nullable=True)
    sequence_order = Column(Integer, default=1, nullable=False)
    duration_minutes = Column(Integer, default=30)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    module = relationship("CourseModule", back_populates="lectures")
    materials = relationship("StudyMaterial", back_populates="lecture", cascade="all, delete-orphan")

# 9. study_materials
class StudyMaterial(Base):
    __tablename__ = "study_materials"
    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(180), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # PDF, PPT, DOC, LINK
    file_size_kb = Column(Integer, default=0)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lecture = relationship("Lecture", back_populates="materials")

# 20. lecture_progress
class LectureProgress(Base):
    __tablename__ = "lecture_progress"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lecture_id = Column(Integer, ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False)
    is_completed = Column(Boolean, default=True, nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("student_id", "lecture_id", name="uq_student_lecture_progress"),)

# 11. assignments
class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(180), nullable=False)
    instructions = Column(Text, nullable=False)
    attachment_url = Column(String(500), nullable=True)
    max_marks = Column(Float, default=100.0, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    allow_late = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")

# 12. submissions
class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    submission_text = Column(Text, nullable=True)
    file_url = Column(String(500), nullable=True)
    status = Column(String(30), default="Submitted")  # Pending, Submitted, Under Review, Evaluated, Late Submission
    version = Column(Integer, default=1)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User")
    feedback = relationship("AssignmentFeedback", back_populates="submission", uselist=False, cascade="all, delete-orphan")

# 13. assignment_feedback
class AssignmentFeedback(Base):
    __tablename__ = "assignment_feedback"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), unique=True, nullable=False)
    evaluator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    marks_obtained = Column(Float, nullable=False)
    comments = Column(Text, nullable=True)
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())

    submission = relationship("Submission", back_populates="feedback")

# 14. quizzes
class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(180), nullable=False)
    description = Column(Text, nullable=True)
    total_marks = Column(Float, default=10.0, nullable=False)
    passing_marks = Column(Float, default=5.0, nullable=False)
    duration_minutes = Column(Integer, default=15, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    allow_retake = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")

# 15. questions
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    marks = Column(Float, default=1.0, nullable=False)

    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("QuizOption", back_populates="question", cascade="all, delete-orphan")

# 16. quiz_options
class QuizOption(Base):
    __tablename__ = "quiz_options"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    option_text = Column(String(500), nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)

    question = relationship("Question", back_populates="options")

# 17. quiz_attempts
class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, default=0.0, nullable=False)
    passed = Column(Boolean, default=False, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)

    quiz = relationship("Quiz", back_populates="attempts")
    student = relationship("User")
    answers = relationship("QuizAnswer", back_populates="attempt", cascade="all, delete-orphan")

# 18. quiz_answers
class QuizAnswer(Base):
    __tablename__ = "quiz_answers"
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    selected_option_id = Column(Integer, ForeignKey("quiz_options.id", ondelete="SET NULL"), nullable=True)
    is_correct = Column(Boolean, default=False)

    attempt = relationship("QuizAttempt", back_populates="answers")

# 19. attendance
class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)  # Present, Absent, Approved Leave, Holiday
    remarks = Column(String(255), nullable=True)
    marked_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint("batch_id", "student_id", "session_date", name="uq_batch_student_date"),)

# 21. certificates
class Certificate(Base):
    __tablename__ = "certificates"
    id = Column(Integer, primary_key=True, index=True)
    certificate_number = Column(String(60), unique=True, index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    issued_date = Column(Date, server_default=func.current_date(), nullable=False)
    pdf_url = Column(String(500), nullable=True)

    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uq_student_course_certificate"),)

    student = relationship("User")
    course = relationship("Course")

# 22. payments
class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String(60), unique=True, index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False)
    total_fee = Column(Float, nullable=False)
    amount_paid = Column(Float, nullable=False)
    pending_amount = Column(Float, nullable=False)
    payment_method = Column(String(50), default="UPI / Bank Transfer")
    status = Column(String(30), default="Paid")  # Paid, Partially Paid, Pending, Failed, Refunded
    notes = Column(String(255), nullable=True)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User")
    course = relationship("Course")

# 23. notifications
class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(180), nullable=False)
    message = Column(Text, nullable=False)
    event_type = Column(String(50), default="General")
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")

# 24. announcements
class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(180), nullable=False)
    content = Column(Text, nullable=False)
    target_role = Column(String(30), default="All")  # All, Admin, Instructor, Student
    batch_id = Column(Integer, ForeignKey("batches.id", ondelete="SET NULL"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
