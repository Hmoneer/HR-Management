"""
Schemas الخاصة بالجزاءات والمكافآت
"""
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.penalty_reward import RecordType


class PenaltyRewardCreate(BaseModel):
    user_id: int
    type: RecordType
    amount: Decimal
    reason: str
    date: date


class PenaltyRewardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    type: RecordType
    amount: Decimal
    reason: str
    date: date
    created_by_id: int
    created_at: datetime
