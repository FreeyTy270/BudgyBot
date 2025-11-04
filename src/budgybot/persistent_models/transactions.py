from datetime import date
from decimal import Decimal
from typing import Annotated, TYPE_CHECKING

from pydantic import computed_field
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from budgybot.persistent_models.banks import BankAccount


# noinspection PyNestedDecorators
class Transaction(SQLModel, table=True):
    """Model that gets saved and fetched from the database. Represents a single row
    of a bank csv archive."""

    id: Annotated[int | None, Field(default=None, primary_key=True)]
    transaction_date: Annotated[date, Field(alias="Transaction Date")]
    amount: Annotated[Decimal, Field(alias="Amount")]
    description: Annotated[str, Field(alias="Description")]
    transaction_type: Annotated[str, Field(alias="Transaction Type")]

    bank_account_name: Annotated[str, Field(foreign_key="bankaccount.account_name")]
    bank_account: Annotated[str, Relationship(back_populates="transactions")]

    @computed_field
    @property
    def transaction_id(self) -> int | None:
        tx_id = None
        if "ID:" in self.description:
            desc_split = self.description.split("ID:")
            self.description = desc_split[0]
            tx_id = int(desc_split[1])
        return tx_id


class ConsumedStatement(SQLModel, table=True):
    id: Annotated[int | None, Field(default=None, primary_key=True)]
    file_name: Annotated[str, Field(alias="File Name")]
    report_date: Annotated[date, Field(alias="Report Date")]
    bank_account: Annotated["BankAccount", Relationship()]


class MonthlyRecurringTransaction(Transaction, table=True):
    day_of_month: Annotated[int, Field(alias="Day Of Month")]
