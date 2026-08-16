"""
عمليات قاعدة البيانات الخاصة بالحضور والانصراف
"""
from datetime import date

from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate


def create_attendance(db: Session, data: AttendanceCreate) -> Attendance:
    record = Attendance(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_attendance(db: Session, attendance_id: int) -> Attendance | None:
    return db.query(Attendance).filter(Attendance.id == attendance_id).first()


def list_attendance(
    db: Session,
    user_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = 0,
    limit: int = 200,
) -> list[Attendance]:
    query = db.query(Attendance)
    if user_id is not None:
        query = query.filter(Attendance.user_id == user_id)
    if date_from is not None:
        query = query.filter(Attendance.date >= date_from)
    if date_to is not None:
        query = query.filter(Attendance.date <= date_to)
    return query.order_by(Attendance.date.desc()).offset(skip).limit(limit).all()


def update_attendance(db: Session, record: Attendance, data: AttendanceUpdate) -> Attendance:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


def delete_attendance(db: Session, record: Attendance) -> None:
    db.delete(record)
    db.commit()


def count_absences(db: Session, user_id: int, month: int, year: int) -> int:
    """عدّ أيام الغياب لموظف معين خلال شهر محدد - يُستخدم في حساب الراتب"""
    from calendar import monthrange
    from app.models.attendance import AttendanceStatus

    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    return (
        db.query(Attendance)
        .filter(
            Attendance.user_id == user_id,
            Attendance.status == AttendanceStatus.ABSENT,
            Attendance.date >= first_day,
            Attendance.date <= last_day,
        )
        .count()
    )
