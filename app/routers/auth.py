"""
راوتر المصادقة: تسجيل الدخول والحصول على بيانات المستخدم الحالي
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.permissions import get_current_user
from app.core.security import create_access_token, verify_password
from app.crud.user import get_user_by_username
from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["المصادقة (Auth)"])


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """تسجيل الدخول باستخدام اسم المستخدم وكلمة المرور، يُعيد JWT access token"""
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="اسم المستخدم أو كلمة المرور غير صحيحة",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="هذا الحساب غير مُفعّل")

    access_token = create_access_token(data={"sub": user.username, "role": user.role.value})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """إرجاع بيانات المستخدم المسجل دخوله حاليًا"""
    return current_user
