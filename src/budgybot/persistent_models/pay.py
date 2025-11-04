from datetime import date
from enum import StrEnum

from sqlmodel import SQLModel


class PayFrequencyUnit(StrEnum):
    DAY = "days"
    WEEK = "weeks"
    MONTH = "months"


class Salary(SQLModel, table=True):
    yearly: float
    monthly: float
    per_pay_period: float


class Pay(SQLModel, table=True):
    amount: float
    frequency: int
    frequency_unit: str
    last_pay_day: date
