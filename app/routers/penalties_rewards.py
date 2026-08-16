"""
راوتر الجزاءات والمكافآت
الصلاحيات:
- الإضافة والحذف: المدير، نائب المدير، الـ HR، المحاسب
- العرض: الإدارة/HR/المحاسب يرون الجميع، والموظف يرى سجلاته فقط
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import (
    CAN_MANAGE_PENALTIES_REWARDS,
    get_current_user,
    require_roles,
)
from app.crud import penalty_reward as pr_crud
from app.database import get_db
from app.models.user import User
from app.schemas.penalty_reward import PenaltyRewardCreate, PenaltyRewardOut

router = APIRouter(prefix="/penalties-rewards", tags=["الجزاءات والمكافآت (Penalties & Rewards)"])


@router.post("/", response_model=PenaltyRewardOut, status_code=status.HTTP_201_CREATED)
def create_record(
    data: PenaltyRewardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*CAN_MANAGE_PENALTIES_REWARDS)),
):
    return pr_crud.create_penalty_reward(db, data, created_by_id=current_user.id)


@router.get("/", response_model=list[PenaltyRewardOut])
def list_records(
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # الموظف العادي يرى سجلاته فقط
    if current_user.role not in CAN_MANAGE_PENALTIES_REWARDS:
        user_id = current_user.id
    return pr_crud.list_penalties_rewards(db, user_id=user_id)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*CAN_MANAGE_PENALTIES_REWARDS)),
):
    record = pr_crud.get_penalty_reward(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="السجل غير موجود")
    pr_crud.delete_penalty_reward(db, record)
