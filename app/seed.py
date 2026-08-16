"""
إنشاء أول حساب مدير تلقائيًا عند أول تشغيل للتطبيق إن لم يوجد أي مستخدم بعد
"""
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole


def seed_first_admin(db: Session) -> None:
    has_any_user = db.query(User).first() is not None
    if has_any_user:
        return

    admin = User(
        username=settings.FIRST_ADMIN_USERNAME,
        email=settings.FIRST_ADMIN_EMAIL,
        full_name=settings.FIRST_ADMIN_FULL_NAME,
        role=UserRole.MANAGER,
        base_salary=0,
        hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
        is_active=True,
    )
    db.add(admin)
    db.commit()
    print(
        f"[seed] تم إنشاء حساب المدير الأول -> username: {settings.FIRST_ADMIN_USERNAME} "
        f"| password: {settings.FIRST_ADMIN_PASSWORD} (يُرجى تغييرها فورًا)"
    )
