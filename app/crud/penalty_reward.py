"""
عمليات قاعدة البيانات الخاصة بالجزاءات والمكافآت
"""
from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.penalty_reward import PenaltyReward, RecordType
from app.schemas.penalty_reward import PenaltyRewardCreate


def create_penalty_reward(db: Session, data: PenaltyRewardCreate, created_by_id: int) -> PenaltyReward:
    record = PenaltyReward(**data.model_dump(), created_by_id=created_by_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_penalty_reward(db: Session, record_id: int) -> PenaltyReward | None:
    return db.query(PenaltyReward).filter(PenaltyReward.id == record_id).first()


def list_penalties_rewards(
    db: Session,
    user_id: int | None = None,
    skip: int = 0,
    limit: int = 200,
) -> list[PenaltyReward]:
    query = db.query(PenaltyReward)
    if user_id is not None:
        query = query.filter(PenaltyReward.user_id == user_id)
    return query.order_by(PenaltyReward.date.desc()).offset(skip).limit(limit).all()


def delete_penalty_reward(db: Session, record: PenaltyReward) -> None:
    db.delete(record)
    db.commit()


def sum_by_type_for_month(db: Session, user_id: int, record_type: RecordType, month: int, year: int) -> Decimal:
    """جمع قيم الجزاءات أو المكافآت لموظف خلال شهر محدد - يُستخدم في حساب الراتب"""
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    records = (
        db.query(PenaltyReward)
        .filter(
            PenaltyReward.user_id == user_id,
            PenaltyReward.type == record_type,
            PenaltyReward.date >= first_day,
            PenaltyReward.date <= last_day,
        )
        .all()
    )
    return sum((r.amount for r in records), Decimal("0"))
