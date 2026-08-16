"""
إعدادات التطبيق العامة (Application Settings)
تُقرأ من متغيرات البيئة أو من ملف .env
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # قاعدة البيانات
    DATABASE_URL: str = "sqlite:///./hr_system.db"

    # إعدادات JWT
    SECRET_KEY: str = "change-this-secret-key-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # حساب المدير الأول (يُنشأ تلقائيًا عند أول تشغيل إن لم توجد بيانات)
    FIRST_ADMIN_USERNAME: str = "admin"
    FIRST_ADMIN_PASSWORD: str = "Admin@12345"
    FIRST_ADMIN_FULL_NAME: str = "System Manager"
    FIRST_ADMIN_EMAIL: str = "admin@company.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
