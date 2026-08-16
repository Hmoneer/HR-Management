"""
راوتر الحضور والانصراف
الصلاحيات:
- تسجيل حضور/انصراف نفسه: أي موظف مسجل دخوله
- إدارة سجلات الحضور لأي موظف (إضافة/تعديل/حذف يدوي): المدير، نائب المدير، الـ HR
- عرض السجلات: الإدارة/HR يرون الجميع، والموظف يرى سجلاته فقط
"""
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import CAN_MANAGE_ATTENDANCE, get_current_user, require_roles
from app.crud import attendance as attendance_crud
from app.database import get_db
from app.models.attendance import AttendanceStatus
from app.models.user import User
from app.schemas.attendance import AttendanceCreate, AttendanceOut, AttendanceUpdate

router = APIRouter(prefix="/attendance", tags=["الحضور والانصراف (Attendance)"])


@router.post("/check-in", response_model=AttendanceOut)
def check_in(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """تسجيل حضور اليوم للمستخدم الحالي"""
    today = date.today()
    existing = next(
        (r for r in attendance_crud.list_attendance(db, user_id=current_user.id, date_from=today, date_to=today)),
        None,
    )
    if existing:
        raise HTTPException(status_code=400, detail="تم تسجيل الحضور اليوم بالفعل")

    data = AttendanceCreate(
        user_id=current_user.id,
        date=today,
        status=AttendanceStatus.PRESENT,
        check_in=datetime.now(),
    )
    return attendance_crud.create_attendance(db, data)


@router.post("/check-out", response_model=AttendanceOut)
def check_out(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """تسجيل انصراف اليوم للمستخدم الحالي"""
    today = date.today()
    records = attendance_crud.list_attendance(db, user_id=current_user.id, date_from=today, date_to=today)
    if not records:
        raise HTTPException(status_code=400, detail="لم يتم تسجيل حضور اليوم بعد")

    record = records[0]
    if record.check_out is not None:
        raise HTTPException(status_code=400, detail="تم تسجيل الانصراف اليوم بالفعل")

    return attendance_crud.update_attendance(db, record, AttendanceUpdate(check_out=datetime.now()))


@router.post("/", response_model=AttendanceOut, status_code=status.HTTP_201_CREATED)
def create_attendance_record(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*CAN_MANAGE_ATTENDANCE)),
):
    """إضافة سجل حضور/غياب يدويًا لموظف معين (استخدام إداري)"""
    return attendance_crud.create_attendance(db, data)


@router.get("/", response_model=list[AttendanceOut])
def list_attendance_records(
    user_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # الموظف العادي يرى سجلاته فقط، حتى لو مرّر user_id مختلف
    if current_user.role not in CAN_MANAGE_ATTENDANCE:
        user_id = current_user.id
    return attendance_crud.list_attendance(db, user_id=user_id, date_from=date_from, date_to=date_to)


@router.put("/{attendance_id}", response_model=AttendanceOut)
def update_attendance_record(
    attendance_id: int,
    data: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*CAN_MANAGE_ATTENDANCE)),
):
    record = attendance_crud.get_attendance(db, attendance_id)
    if not record:
        raise HTTPException(status_code=404, detail="السجل غير موجود")
    return attendance_crud.update_attendance(db, record, data)


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance_record(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*CAN_MANAGE_ATTENDANCE)),
):
    record = attendance_crud.get_attendance(db, attendance_id)
    if not record:
        raise HTTPException(status_code=404, detail="السجل غير موجود")
    attendance_crud.delete_attendance(db, record)
