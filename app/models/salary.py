"""
موديل سجل الراتب الشهري لكل موظف
يُحسب في نهاية الشهر بناءً على الراتب الأساسي + المكافآت - الجزاءات - خصم أيام الغياب
"""
from sqlalchemy import (
    Column, Integer, ForeignKey, DateTime, Numeric, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class SalaryRecord(Base):
    __tablename__ = "salary_records"
    __table_args__ = (
        UniqueConstraint("user_id", "month", "year", name="uq_salary_user_month_year"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)

    base_salary = Column(Numeric(12, 2), nullable=False)
    total_rewards = Column(Numeric(12, 2), nullable=False, default=0)
    total_penalties = Column(Numeric(12, 2), nullable=False, default=0)
    absence_days = Column(Integer, nullable=False, default=0)
    absence_deduction = Column(Numeric(12, 2), nullable=False, default=0)
    net_salary = Column(Numeric(12, 2), nullable=False)

    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="salary_records", foreign_keys=[user_id])
    generated_by = relationship("User", foreign_keys=[generated_by_id])
