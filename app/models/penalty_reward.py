"""
موديل الجزاءات والمكافآت الخاصة بالموظفين
"""
import enum

from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime, Enum, String, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RecordType(str, enum.Enum):
    PENALTY = "penalty"  # جزاء (خصم)
    REWARD = "reward"    # مكافأة (إضافة)


class PenaltyReward(Base):
    __tablename__ = "penalties_rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    type = Column(Enum(RecordType), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    reason = Column(String(255), nullable=False)
    date = Column(Date, nullable=False, index=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="penalties_rewards", foreign_keys=[user_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
