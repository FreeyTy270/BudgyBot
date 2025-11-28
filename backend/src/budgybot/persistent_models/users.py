from sqlmodel import Field, SQLModel


class UserProfile(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    salary: float
#     bank_accounts: list[BankAccount] = Relationship()
