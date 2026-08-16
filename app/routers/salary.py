"""
راوتر الرواتب
الصلاحيات:
- حساب/إنشاء الرواتب الشهرية: المدير، نائب المدير، المحاسب
- عرض الرواتب: الإدارة/المحاسب يرون الجميع، والموظف يرى راتبه فقط
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import CAN_MANAGE_SALARY, get_current_user, require_roles
from app.crud import salary as salary_crud
from app.crud.user import get_user, list_users
from app.database import get_db
from app.models.user import User
from app.schemas.salary import (
    SalaryGenerateAllRequest,
    SalaryGenerateRequest,
    SalaryRecordOut,
)

router = APIRouter(prefix="/salary", tags=["الرواتب (Salary)"])


@router.post("/generate", response_model=SalaryRecordOut)
def generate_salary(
    data: SalaryGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*CAN_MANAGE_SALARY)),
):
    """حساب وإنشاء (أو إعادة حساب) راتب موظف واحد لشهر معين"""
    user = get_user(db, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
    return salary_crud.calculate_and_generate_salary(
        db, user, data.month, data.year, generated_by_id=current_user.id
    )


@router.post("/generate-all", response_model=list[SalaryRecordOut])
def generate_salary_for_all(
    data: SalaryGenerateAllRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*CAN_MANAGE_SALARY)),
):
    """حساب وإنشاء رواتب كل الموظفين النشطين لشهر معين دفعة واحدة (تشغيل نهاية الشهر)"""
    results = []
    for user in list_users(db, limit=10_000):
        if not user.is_active:
            continue
        results.append(
            salary_crud.calculate_and_generate_salary(
                db, user, data.month, data.year, generated_by_id=current_user.id
            )
        )
    return results


@router.get("/", response_model=list[SalaryRecordOut])
def list_salary(
    user_id: int | None = None,
    month: int | None = None,
    year: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # الموظف العادي يرى رواتبه فقط
    if current_user.role not in CAN_MANAGE_SALARY:
        user_id = current_user.id
    return salary_crud.list_salary_records(db, user_id=user_id, month=month, year=year)
