from pydantic import BaseModel
from typing_extensions import Annotated

from sqlmodel import Field, Relationship

from budgybot.persistent_models.banks import BankAccount
from budgybot.persistent_models.transactions import MonthlyRecurringTransaction


class UserProfile(BaseModel):
    id: Annotated[int | None, Field(default=None, primary_key=True)]
    salary: float
    bank_accounts: Annotated[list[BankAccount], Relationship()]
    monthlies: Annotated[list[MonthlyRecurringTransaction], Relationship()]
