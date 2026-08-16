"""
إعداد الاتصال بقاعدة البيانات باستخدام SQLAlchemy
يدعم SQLite افتراضيًا، ويمكن استبدالها بـ PostgreSQL/MySQL عبر DATABASE_URL
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# connect_args خاصة بـ SQLite فقط (للسماح باستخدامها من عدة threads)
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency تُستخدم في مسارات FastAPI لفتح جلسة قاعدة بيانات
    وإغلاقها تلقائيًا بعد انتهاء الطلب
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
