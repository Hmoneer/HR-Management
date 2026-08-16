"""
Dependencies للحصول على المستخدم الحالي والتحقق من صلاحياته حسب الدور الوظيفي
تُستخدم في كل الراوترات لحماية المسارات (Endpoints)
"""
from typing import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="لا يمكن التحقق من بيانات الاعتماد",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="هذا الحساب غير مُفعّل")
    return user


def require_roles(*allowed_roles: Iterable[UserRole]):
    """
    مصنع Dependencies: يسمح فقط للمستخدمين الذين يملكون أحد الأدوار المحددة
    مثال الاستخدام: Depends(require_roles(UserRole.MANAGER, UserRole.HR))
    """
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ليس لديك صلاحية للقيام بهذا الإجراء",
            )
        return current_user

    return dependency


# مجموعات صلاحيات جاهزة يُعاد استخدامها في الراوترات المختلفة
IS_MANAGEMENT = (UserRole.MANAGER, UserRole.DEPUTY_MANAGER)
CAN_MANAGE_EMPLOYEES = (UserRole.MANAGER, UserRole.DEPUTY_MANAGER, UserRole.HR)
CAN_MANAGE_ATTENDANCE = (UserRole.MANAGER, UserRole.DEPUTY_MANAGER, UserRole.HR)
CAN_MANAGE_PENALTIES_REWARDS = (UserRole.MANAGER, UserRole.DEPUTY_MANAGER, UserRole.HR, UserRole.ACCOUNTANT)
CAN_MANAGE_SALARY = (UserRole.MANAGER, UserRole.DEPUTY_MANAGER, UserRole.ACCOUNTANT)
