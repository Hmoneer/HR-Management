"""
Schemas الخاصة بالحضور والانصراف
"""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.attendance import AttendanceStatus


class AttendanceCreate(BaseModel):
    user_id: int
    date: date
    status: AttendanceStatus = AttendanceStatus.PRESENT
    check_in: datetime | None = None
    check_out: datetime | None = None
    notes: str | None = None


class AttendanceUpdate(BaseModel):
    status: AttendanceStatus | None = None
    check_in: datetime | None = None
    check_out: datetime | None = None
    notes: str | None = None


class AttendanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date: date
    status: AttendanceStatus
    check_in: datetime | None
    check_out: datetime | None
    notes: str | None
