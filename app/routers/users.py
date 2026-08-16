"""
راوتر إدارة المستخدمين (الموظفين)
الصلاحيات:
- العرض والإنشاء والتعديل: المدير، نائب المدير، الـ HR
- تعيين دور "مدير" لمستخدم جديد أو حذف مستخدم: المدير فقط
- كل موظف يمكنه رؤية بياناته الخاصة عبر /auth/me
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.permissions import CAN_MANAGE_EMPLOYEES, get_current_user, require_roles
from app.crud import user as user_crud
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["الموظفون (Users)"])


@router.get("/", response_model=list[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*CAN_MANAGE_EMPLOYEES)),
):
    return user_crud.list_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # يسمح للموظف برؤية بياناته فقط، وللإدارة/HR برؤية أي موظف
    if current_user.id != user_id and current_user.role not in CAN_MANAGE_EMPLOYEES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ليس لديك صلاحية")
    db_user = user_crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
    return db_user


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*CAN_MANAGE_EMPLOYEES)),
):
    # فقط المدير يمكنه إنشاء حساب مدير أو نائب مدير جديد
    if user_in.role in (UserRole.MANAGER, UserRole.DEPUTY_MANAGER) and current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="فقط المدير يمكنه إنشاء هذا النوع من الحسابات")

    if user_crud.get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="اسم المستخدم مستخدم بالفعل")
    if user_crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="البريد الإلكتروني مستخدم بالفعل")

    try:
        return user_crud.create_user(db, user_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="تعذر إنشاء المستخدم، تحقق من البيانات")


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*CAN_MANAGE_EMPLOYEES)),
):
    db_user = user_crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")

    if user_in.role and current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="فقط المدير يمكنه تغيير الدور الوظيفي")

    return user_crud.update_user(db, db_user, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.MANAGER)),
):
    db_user = user_crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
    if db_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="لا يمكنك حذف حسابك الخاص")
    user_crud.delete_user(db, db_user)
