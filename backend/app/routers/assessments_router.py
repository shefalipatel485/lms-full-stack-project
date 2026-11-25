from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.lms_models import (
    Assignment, Submission, AssignmentFeedback, Quiz, Question,
    QuizOption, QuizAttempt, QuizAnswer, Enrollment, User
)
from app.schemas.lms_schemas import (
    AssignmentCreate, SubmissionCreate, EvaluationCreate,
    QuizCreate, QuizAttemptSubmit
)
from app.dependencies.auth_deps import get_current_user, require_roles

router = APIRouter(prefix="/api", tags=["Assignments & Quizzes"])

# --- ASSIGNMENTS ---
@router.get("/assignments")
def list_assignments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    role = current_user.role.name
    query = db.query(Assignment)
    if role == "student":
        cids = [e.course_id for e in db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()]
        query = query.filter(Assignment.course_id.in_(cids))

    assignments = query.order_by(Assignment.id.desc()).all()
    results = []
    for a in assignments:
        my_sub = None
        if role == "student":
            sub = db.query(Submission).filter(
                Submission.assignment_id == a.id,
                Submission.student_id == current_user.id
            ).first()
            if sub:
                my_sub = {
                    "id": sub.id,
                    "status": sub.status,
                    "submission_text": sub.submission_text,
                    "file_url": sub.file_url,
                    "submitted_at": sub.submitted_at,
                    "marks_obtained": sub.feedback.marks_obtained if sub.feedback else None,
                    "comments": sub.feedback.comments if sub.feedback else None
                }
        results.append({
            "id": a.id,
            "course_id": a.course_id,
            "batch_id": a.batch_id,
            "title": a.title,
            "instructions": a.instructions,
            "max_marks": a.max_marks,
            "due_date": a.due_date,
            "allow_late": a.allow_late,
            "submissions_count": len(a.submissions),
            "my_submission": my_sub
        })
    return results

@router.post("/assignments", status_code=201)
def create_assignment(
    payload: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "instructor"]))
):
    asg = Assignment(**payload.model_dump(), created_by=current_user.id)
    db.add(asg)
    db.commit()
    db.refresh(asg)
    return {"id": asg.id, "title": asg.title}

@router.get("/assignments/{assignment_id}/submissions")
def list_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["admin", "instructor"]))
):
    subs = db.query(Submission).filter(Submission.assignment_id == assignment_id).all()
    return [
        {
            "id": s.id,
            "student_id": s.student_id,
            "student_name": s.student.full_name if s.student else "Student",
            "submission_text": s.submission_text,
            "file_url": s.file_url,
            "status": s.status,
            "submitted_at": s.submitted_at,
            "marks_obtained": s.feedback.marks_obtained if s.feedback else None,
            "comments": s.feedback.comments if s.feedback else None
        }
        for s in subs
    ]

@router.post("/submissions", status_code=201)
def submit_assignment(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["student"]))
):
    asg = db.query(Assignment).filter(Assignment.id == payload.assignment_id).first()
    if not asg:
        raise HTTPException(status_code=404, detail="Assignment not found")

    now = datetime.now(timezone.utc)
    due = asg.due_date if asg.due_date.tzinfo else asg.due_date.replace(tzinfo=timezone.utc)
    is_late = now > due
    if is_late and not asg.allow_late:
        raise HTTPException(status_code=400, detail="Deadline passed and late submissions are disabled")

    existing = db.query(Submission).filter(
        Submission.assignment_id == payload.assignment_id,
        Submission.student_id == current_user.id
    ).first()
    if existing:
        existing.submission_text = payload.submission_text
        existing.file_url = payload.file_url
        existing.version += 1
        existing.status = "Late Submission" if is_late else "Submitted"
        existing.submitted_at = now
        db.commit()
        return {"id": existing.id, "status": existing.status, "version": existing.version}

    sub = Submission(
        assignment_id=payload.assignment_id,
        student_id=current_user.id,
        submission_text=payload.submission_text,
        file_url=payload.file_url,
        status="Late Submission" if is_late else "Submitted"
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return {"id": sub.id, "status": sub.status}

@router.post("/submissions/{submission_id}/evaluate")
def evaluate_submission(
    submission_id: int,
    payload: EvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "instructor"]))
):
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    if payload.marks_obtained > sub.assignment.max_marks:
        raise HTTPException(status_code=400, detail=f"Marks cannot exceed {sub.assignment.max_marks}")

    if sub.feedback:
        sub.feedback.marks_obtained = payload.marks_obtained
        sub.feedback.comments = payload.comments
        sub.feedback.evaluator_id = current_user.id
    else:
        db.add(AssignmentFeedback(
            submission_id=sub.id,
            evaluator_id=current_user.id,
            marks_obtained=payload.marks_obtained,
            comments=payload.comments
        ))
    sub.status = "Evaluated"
    db.commit()
    return {"message": "Submission evaluated", "status": "Evaluated"}

# --- QUIZZES ---
@router.get("/quizzes")
def list_quizzes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    role = current_user.role.name
    query = db.query(Quiz)
    if role == "student":
        cids = [e.course_id for e in db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()]
        query = query.filter(Quiz.course_id.in_(cids))

    quizzes = query.order_by(Quiz.id.desc()).all()
    out = []
    for q in quizzes:
        attempts = db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == q.id,
            QuizAttempt.student_id == current_user.id
        ).all() if role == "student" else []

        # SECURITY RULE (Section 5.8): Never expose is_correct to students before submission
        questions_data = []
        for ques in q.questions:
            opts = []
            for opt in ques.options:
                opt_dict = {"id": opt.id, "option_text": opt.option_text}
                if role in ["admin", "instructor"]:
                    opt_dict["is_correct"] = opt.is_correct
                opts.append(opt_dict)
            questions_data.append({
                "id": ques.id,
                "question_text": ques.question_text,
                "marks": ques.marks,
                "options": opts
            })

        out.append({
            "id": q.id,
            "course_id": q.course_id,
            "batch_id": q.batch_id,
            "title": q.title,
            "description": q.description,
            "total_marks": q.total_marks,
            "passing_marks": q.passing_marks,
            "duration_minutes": q.duration_minutes,
            "allow_retake": q.allow_retake,
            "questions_count": len(q.questions),
            "questions": questions_data,
            "my_attempts": [
                {"id": at.id, "score": at.score, "passed": at.passed, "submitted_at": at.submitted_at}
                for at in attempts
            ]
        })
    return out

@router.post("/quizzes", status_code=201)
def create_quiz(
    payload: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "instructor"]))
):
    total_marks = sum(q.marks for q in payload.questions)
    quiz = Quiz(
        course_id=payload.course_id,
        batch_id=payload.batch_id,
        title=payload.title,
        description=payload.description,
        total_marks=total_marks,
        passing_marks=payload.passing_marks,
        duration_minutes=payload.duration_minutes,
        allow_retake=payload.allow_retake,
        created_by=current_user.id
    )
    db.add(quiz)
    db.flush()

    for q_item in payload.questions:
        ques = Question(quiz_id=quiz.id, question_text=q_item.question_text, marks=q_item.marks)
        db.add(ques)
        db.flush()
        for opt in q_item.options:
            db.add(QuizOption(question_id=ques.id, option_text=opt.option_text, is_correct=opt.is_correct))

    db.commit()
    db.refresh(quiz)
    return {"id": quiz.id, "title": quiz.title, "total_marks": quiz.total_marks}

@router.post("/quizzes/{quiz_id}/attempt", status_code=201)
def submit_quiz_attempt(
    quiz_id: int,
    payload: QuizAttemptSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["student"]))
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    prev_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == current_user.id
    ).count()
    if prev_attempts > 0 and not quiz.allow_retake:
        raise HTTPException(status_code=409, detail="Retakes are not enabled for this quiz")

    # Server-side score calculation (Section 5.8)
    answer_map = {a.question_id: a.selected_option_id for a in payload.answers}
    score = 0.0
    attempt = QuizAttempt(
        quiz_id=quiz.id,
        student_id=current_user.id,
        score=0.0,
        passed=False,
        submitted_at=datetime.now(timezone.utc)
    )
    db.add(attempt)
    db.flush()

    review = []
    for ques in quiz.questions:
        selected_id = answer_map.get(ques.id)
        correct_opt = next((o for o in ques.options if o.is_correct), None)
        is_right = (selected_id is not None and correct_opt is not None and selected_id == correct_opt.id)
        if is_right:
            score += ques.marks

        db.add(QuizAnswer(
            attempt_id=attempt.id,
            question_id=ques.id,
            selected_option_id=selected_id,
            is_correct=is_right
        ))
        review.append({
            "question_id": ques.id,
            "question_text": ques.question_text,
            "selected_option_id": selected_id,
            "correct_option_id": correct_opt.id if correct_opt else None,
            "is_correct": is_right
        })

    attempt.score = score
    attempt.passed = score >= quiz.passing_marks
    db.commit()

    return {
        "attempt_id": attempt.id,
        "score": score,
        "total_marks": quiz.total_marks,
        "passing_marks": quiz.passing_marks,
        "passed": attempt.passed,
        "review": review
    }
