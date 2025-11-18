from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from budgybot.utils.helper_enums import AccountType

if TYPE_CHECKING:
    from budgybot.persistent_models.transactions import Transaction


class Bank(SQLModel, table=True):
    name: str = Field(primary_key=True)
    accounts: list["BankAccount"] = Relationship(back_populates="bank")


class BankAccount(SQLModel, table=True):
    account_name: str = Field(primary_key=True)
    bank_name: str = Field(foreign_key="bank.name")
    bank: "Bank" = Relationship(back_populates="accounts")
    account_type: AccountType = Field(alias="Account Type", nullable=False)
    transactions: list["Transaction"] = Relationship(back_populates="bank_account")
    estimated_balance: float = Field(alias="Estimated Account Balance")
