"""
موديل المستخدم (الموظف) وتعريف الأدوار الوظيفية داخل النظام
"""
import enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserRole(str, enum.Enum):
    """الأدوار الوظيفية المدعومة في النظام"""
    MANAGER = "manager"                # المدير - صلاحيات كاملة
    DEPUTY_MANAGER = "deputy_manager"  # نائب المدير - صلاحيات شبه كاملة
    ACCOUNTANT = "accountant"          # المحاسب - يدير الرواتب والجزاءات/المكافآت المالية
    HR = "hr"                          # الموارد البشرية - يدير الحضور والانصراف وبيانات الموظفين
    EMPLOYEE = "employee"              # الموظف العادي - يرى بياناته الخاصة فقط


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    phone = Column(String(30), nullable=True)
    hashed_password = Column(String(255), nullable=False)

    role = Column(Enum(UserRole), nullable=False, default=UserRole.EMPLOYEE)

    # الراتب الأساسي الشهري، يُستخدم في حساب راتب نهاية الشهر
    base_salary = Column(Numeric(12, 2), nullable=False, default=0)

    hire_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # علاقات مرتبطة بهذا المستخدم
    attendances = relationship(
        "Attendance", back_populates="user", cascade="all, delete-orphan",
        foreign_keys="Attendance.user_id",
    )
    penalties_rewards = relationship(
        "PenaltyReward", back_populates="user", cascade="all, delete-orphan",
        foreign_keys="PenaltyReward.user_id",
    )
    salary_records = relationship(
        "SalaryRecord", back_populates="user", cascade="all, delete-orphan",
        foreign_keys="SalaryRecord.user_id",
    )
