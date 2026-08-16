"""
Schemas الخاصة بحساب وعرض الرواتب الشهرية
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SalaryGenerateRequest(BaseModel):
    user_id: int
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)


class SalaryGenerateAllRequest(BaseModel):
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)


class SalaryRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    month: int
    year: int
    base_salary: Decimal
    total_rewards: Decimal
    total_penalties: Decimal
    absence_days: int
    absence_deduction: Decimal
    net_salary: Decimal
    generated_by_id: int
    generated_at: datetime
