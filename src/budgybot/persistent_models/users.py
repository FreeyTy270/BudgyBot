from sqlmodel import SQLModel, Field, Relationship

from budgybot.persistent_models.banks import BankAccount


class UserProfile(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    salary: float
    bank_accounts: list[BankAccount] = Relationship()
