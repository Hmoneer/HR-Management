"""
نقطة انطلاق التطبيق - نظام إدارة الموارد البشرية (HR Management System)
يربط كل الراوترات ببعضها وينشئ جداول قاعدة البيانات عند الإقلاع
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.routers import attendance, auth, penalties_rewards, salary, users
from app.seed import seed_first_admin

app = FastAPI(
    title="نظام إدارة الموارد البشرية | HR Management System",
    description=(
        "نظام متكامل لإدارة الهيكل الإداري بين الإدارة والعاملين: "
        "المصادقة والصلاحيات، الحضور والانصراف، الجزاءات والمكافآت، وحساب الرواتب الشهرية."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # إنشاء جداول قاعدة البيانات إن لم تكن موجودة
    Base.metadata.create_all(bind=engine)

    # إنشاء أول حساب مدير تلقائيًا إن كانت قاعدة البيانات فارغة
    db = SessionLocal()
    try:
        seed_first_admin(db)
    finally:
        db.close()


# ربط كل الراوترات بالتطبيق الرئيسي
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(attendance.router)
app.include_router(penalties_rewards.router)
app.include_router(salary.router)


@app.get("/", tags=["الصفحة الرئيسية (Root)"])
def root():
    return {
        "message": "مرحبًا بك في نظام إدارة الموارد البشرية",
        "docs": "/docs",
        "redoc": "/redoc",
    }
