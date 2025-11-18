from datetime import date
from enum import StrEnum
from typing import Optional

from sqlmodel import SQLModel, Field


class PayFrequencyUnit(StrEnum):
    DAY = "days"
    WEEK = "weeks"
    MONTH = "months"


class Salary(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    yearly: float
    monthly: float
    per_pay_period: float


class Pay(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    frequency: int
    frequency_unit: str
    last_pay_day: date
