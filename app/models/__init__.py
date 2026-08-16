"""
تجميع كل الموديلات في مكان واحد حتى تتعرف عليها SQLAlchemy
عند تنفيذ Base.metadata.create_all()
"""
from app.models.user import User, UserRole
from app.models.attendance import Attendance, AttendanceStatus
from app.models.penalty_reward import PenaltyReward, RecordType
from app.models.salary import SalaryRecord

__all__ = [
    "User",
    "UserRole",
    "Attendance",
    "AttendanceStatus",
    "PenaltyReward",
    "RecordType",
    "SalaryRecord",
]
