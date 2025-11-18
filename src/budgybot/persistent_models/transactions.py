from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from budgybot.persistent_models.banks import BankAccount


# noinspection PyNestedDecorators
class Transaction(SQLModel, table=True):
    """Model that gets saved and fetched from the database. Represents a single row
    of a bank csv archive."""

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_date: date = Field(alias="Transaction Date")
    amount: Decimal = Field(alias="Amount")
    description: str = Field(alias="Description")
    transaction_type: str = Field(alias="Transaction Type")

    bank_account_name: str = Field(foreign_key="bankaccount.account_name")
    bank_account: BankAccount = Relationship(back_populates="transactions")

    # @computed_field
    # @property
    # def transaction_id(self) -> int | None:
    #     tx_id = None
    #     if "ID:" in self.description:
    #         desc_split = self.description.split("ID:")
    #         self.description = desc_split[0]
    #         tx_id = int(desc_split[1])
    #     return tx_id


class ConsumedStatement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    file_name: str = Field(alias="File Name")
    report_date: date = Field(alias="Report Date")
