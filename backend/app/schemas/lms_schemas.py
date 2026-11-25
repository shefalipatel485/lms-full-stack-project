from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime, date

# --- Auth & Users ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None
    role_name: str = "student"
    expertise: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    role_name: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str = Field(..., min_length=6)

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# --- Courses & Modules ---
class ModuleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    sequence_order: int = 1

class CourseCreate(BaseModel):
    code: str
    title: str
    description: str
    category: str
    duration_weeks: int = 8
    fee: float = 0.0
    thumbnail_url: Optional[str] = None
    status: str = "Published"
    instructor_id: Optional[int] = None

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    duration_weeks: Optional[int] = None
    fee: Optional[float] = None
    status: Optional[str] = None
    instructor_id: Optional[int] = None

# --- Batches ---
class BatchCreate(BaseModel):
    name: str
    course_id: int
    instructor_id: Optional[int] = None
    start_date: date
    end_date: date
    schedule_timing: str
    capacity: int = 30
    status: str = "Active"

    @field_validator("end_date")
    @classmethod
    def check_dates(cls, v, info):
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("End date must be on or after start date")
        return v

class BatchEnrollStudent(BaseModel):
    student_id: int

# --- Lectures & Study Materials ---
class LectureCreate(BaseModel):
    course_id: int
    module_id: int
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    sequence_order: int = 1
    duration_minutes: int = 30

class StudyMaterialCreate(BaseModel):
    lecture_id: int
    title: str
    file_url: str
    file_type: str = "PDF"
    file_size_kb: int = 120

# --- Assignments & Submissions ---
class AssignmentCreate(BaseModel):
    course_id: int
    batch_id: Optional[int] = None
    title: str
    instructions: str
    attachment_url: Optional[str] = None
    max_marks: float = 100.0
    due_date: datetime
    allow_late: bool = True

class SubmissionCreate(BaseModel):
    assignment_id: int
    submission_text: Optional[str] = None
    file_url: Optional[str] = None

class EvaluationCreate(BaseModel):
    marks_obtained: float = Field(..., ge=0)
    comments: Optional[str] = None

# --- Quizzes ---
class QuizOptionCreate(BaseModel):
    option_text: str
    is_correct: bool = False

class QuestionCreate(BaseModel):
    question_text: str
    marks: float = 1.0
    options: List[QuizOptionCreate]

class QuizCreate(BaseModel):
    course_id: int
    batch_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    passing_marks: float = 5.0
    duration_minutes: int = 15
    allow_retake: bool = False
    questions: List[QuestionCreate]

class QuizAnswerSubmit(BaseModel):
    question_id: int
    selected_option_id: Optional[int] = None

class QuizAttemptSubmit(BaseModel):
    answers: List[QuizAnswerSubmit]

# --- Attendance ---
class AttendanceRecordItem(BaseModel):
    student_id: int
    status: str  # Present, Absent, Approved Leave, Holiday
    remarks: Optional[str] = None

class AttendanceBulkCreate(BaseModel):
    batch_id: int
    session_date: date
    records: List[AttendanceRecordItem]

# --- Payments ---
class PaymentCreate(BaseModel):
    student_id: int
    course_id: int
    total_fee: float
    amount_paid: float
    payment_method: str = "UPI"
    status: str = "Paid"
    notes: Optional[str] = None

# --- Announcements ---
class AnnouncementCreate(BaseModel):
    title: str
    content: str
    target_role: str = "All"
    batch_id: Optional[int] = None
