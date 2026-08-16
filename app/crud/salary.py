"""
عمليات حساب وإنشاء سجلات الرواتب الشهرية
"""
from calendar import monthrange
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.crud.attendance import count_absences
from app.crud.penalty_reward import sum_by_type_for_month
from app.models.penalty_reward import RecordType
from app.models.salary import SalaryRecord
from app.models.user import User


def get_salary_record(db: Session, user_id: int, month: int, year: int) -> SalaryRecord | None:
    return (
        db.query(SalaryRecord)
        .filter(
            SalaryRecord.user_id == user_id,
            SalaryRecord.month == month,
            SalaryRecord.year == year,
        )
        .first()
    )


def list_salary_records(
    db: Session,
    user_id: int | None = None,
    month: int | None = None,
    year: int | None = None,
) -> list[SalaryRecord]:
    query = db.query(SalaryRecord)
    if user_id is not None:
        query = query.filter(SalaryRecord.user_id == user_id)
    if month is not None:
        query = query.filter(SalaryRecord.month == month)
    if year is not None:
        query = query.filter(SalaryRecord.year == year)
    return query.order_by(SalaryRecord.year.desc(), SalaryRecord.month.desc()).all()


def calculate_and_generate_salary(
    db: Session, user: User, month: int, year: int, generated_by_id: int
) -> SalaryRecord:
    """
    حساب راتب الموظف لشهر معين:
    الراتب الصافي = الراتب الأساسي + إجمالي المكافآت - إجمالي الجزاءات - خصم أيام الغياب

    خصم الغياب يُحسب كنسبة من الراتب اليومي (الراتب الأساسي / عدد أيام الشهر) لكل يوم غياب
    """
    days_in_month = monthrange(year, month)[1]
    daily_rate = user.base_salary / Decimal(days_in_month)

    absence_days = count_absences(db, user.id, month, year)
    absence_deduction = (daily_rate * absence_days).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    total_rewards = sum_by_type_for_month(db, user.id, RecordType.REWARD, month, year)
    total_penalties = sum_by_type_for_month(db, user.id, RecordType.PENALTY, month, year)

    net_salary = (
        user.base_salary + total_rewards - total_penalties - absence_deduction
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    existing = get_salary_record(db, user.id, month, year)
    if existing:
        # إعادة الحساب وتحديث السجل الموجود بدل إنشاء سجل مكرر
        existing.base_salary = user.base_salary
        existing.total_rewards = total_rewards
        existing.total_penalties = total_penalties
        existing.absence_days = absence_days
        existing.absence_deduction = absence_deduction
        existing.net_salary = net_salary
        existing.generated_by_id = generated_by_id
        db.commit()
        db.refresh(existing)
        return existing

    record = SalaryRecord(
        user_id=user.id,
        month=month,
        year=year,
        base_salary=user.base_salary,
        total_rewards=total_rewards,
        total_penalties=total_penalties,
        absence_days=absence_days,
        absence_deduction=absence_deduction,
        net_salary=net_salary,
        generated_by_id=generated_by_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
