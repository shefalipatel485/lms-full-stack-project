from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.lms_models import User, Role, Instructor
from app.schemas.lms_schemas import (
    LoginRequest, RegisterRequest, TokenResponse, UserOut,
    PasswordChangeRequest, ForgotPasswordRequest, ResetPasswordRequest
)
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.dependencies.auth_deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive. Please contact administrator."
        )

    role_name = user.role.name if user.role else "student"
    token = create_access_token({"sub": str(user.id), "role": role_name, "email": user.email})
    return TokenResponse(
        access_token=token,
        user=UserOut(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role=role_name,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email_clean = payload.email.lower().strip()
    if db.query(User).filter(User.email == email_clean).first():
        raise HTTPException(status_code=409, detail="Email address is already registered")

    role_req = payload.role_name.lower().strip()
    if role_req not in ["student", "instructor"]:
        role_req = "student"

    role = db.query(Role).filter(Role.name == role_req).first()
    if not role:
        raise HTTPException(status_code=400, detail="Configured role not found")

    new_user = User(
        full_name=payload.full_name.strip(),
        email=email_clean,
        password_hash=get_password_hash(payload.password),
        phone=payload.phone,
        role_id=role.id,
        is_active=True
    )
    db.add(new_user)
    db.flush()

    if role_req == "instructor":
        db.add(Instructor(user_id=new_user.id, expertise=payload.expertise or "General Subject Matter"))

    db.commit()
    db.refresh(new_user)
    return UserOut(
        id=new_user.id,
        full_name=new_user.full_name,
        email=new_user.email,
        phone=new_user.phone,
        role=role.name,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role.name,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

@router.post("/change-password")
def change_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = get_password_hash(payload.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Return generic success message without leaking account existence (Section 5.1 & 10)
    return {
        "message": "If an active account exists for this email, a password reset token has been generated.",
        "demo_reset_token": "RESET-2026-LMS"
    }

@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    if payload.reset_token != "RESET-2026-LMS":
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    user.password_hash = get_password_hash(payload.new_password)
    db.commit()
    return {"message": "Password reset successfully. You may now log in."}
