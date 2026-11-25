from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.lms_models import User, Role, Instructor
from app.schemas.lms_schemas import RegisterRequest, UserUpdate, UserOut
from app.utils.security import get_password_hash
from app.dependencies.auth_deps import get_current_user, require_roles

router = APIRouter(prefix="/api/users", tags=["Users & Students Management"])

@router.get("")
def list_users(
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "instructor"]))
):
    query = db.query(User).join(Role)
    if current_user.role.name == "instructor":
        query = query.filter(Role.name == "student")
    elif role:
        query = query.filter(Role.name == role.lower())

    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter((User.full_name.ilike(term)) | (User.email.ilike(term)))

    users = query.order_by(User.id.desc()).all()
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "phone": u.phone,
            "role": u.role.name,
            "is_active": u.is_active,
            "created_at": u.created_at
        }
        for u in users
    ]

@router.post("", status_code=201)
def create_user_by_admin(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["admin"]))
):
    email_clean = payload.email.lower().strip()
    if db.query(User).filter(User.email == email_clean).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    role = db.query(Role).filter(Role.name == payload.role_name.lower()).first()
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role specified")

    user = User(
        full_name=payload.full_name,
        email=email_clean,
        password_hash=get_password_hash(payload.password),
        phone=payload.phone,
        role_id=role.id,
        is_active=True
    )
    db.add(user)
    db.flush()
    if role.name == "instructor":
        db.add(Instructor(user_id=user.id, expertise=payload.expertise or "Academic Trainer"))
    db.commit()
    return {"id": user.id, "full_name": user.full_name, "email": user.email, "role": role.name, "is_active": user.is_active}

@router.put("/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.name != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot modify another user's profile")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.phone is not None:
        user.phone = payload.phone
    if current_user.role.name == "admin":
        if payload.is_active is not None:
            user.is_active = payload.is_active
        if payload.role_name is not None:
            role = db.query(Role).filter(Role.name == payload.role_name.lower()).first()
            if role:
                user.role_id = role.id

    db.commit()
    return {"message": "User updated successfully", "id": user.id}

@router.delete("/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["admin"]))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": f"User {user.email} deactivated"}
