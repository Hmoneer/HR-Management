"""
موديل الحضور والانصراف
"""
import enum

from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime, Enum, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"    # حاضر
    ABSENT = "absent"      # غائب
    LATE = "late"          # متأخر
    LEAVE = "leave"        # إجازة


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    date = Column(Date, nullable=False, index=True)
    check_in = Column(DateTime(timezone=True), nullable=True)
    check_out = Column(DateTime(timezone=True), nullable=True)

    status = Column(Enum(AttendanceStatus), nullable=False, default=AttendanceStatus.PRESENT)
    notes = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="attendances", foreign_keys=[user_id])
