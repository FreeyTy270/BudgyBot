from __future__ import annotations
from typing import Annotated, TYPE_CHECKING


from sqlmodel import SQLModel, Field, Relationship

from budgybot.utils.helper_enums import AccountType

if TYPE_CHECKING:
    from budgybot.persistent_models.transactions import Transaction


class Bank(SQLModel, table=True):
    name: Annotated[str, Field(primary_key=True)]
    accounts: Annotated[list[BankAccount], Relationship(back_populates="bank")]


class BankAccount(SQLModel, table=True):
    account_name: Annotated[str, Field(primary_key=True)]
    bank: Annotated[Bank, Relationship(back_populates="accounts")]
    account_type: Annotated[AccountType, Field(alias="Account Type", nullable=False)]
    transactions: Annotated[
        list["Transaction"], Relationship(back_populates="bank_account")
    ]
    estimated_balance: Annotated[float, Field(alias="Estimated Account Balance")]
