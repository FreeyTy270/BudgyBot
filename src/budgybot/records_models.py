from datetime import date
from decimal import Decimal
from typing_extensions import Annotated

from pydantic import computed_field, BaseModel
from sqlmodel import SQLModel, Field

# noinspection PyNestedDecorators
class BankEntry(SQLModel, table=True):
    """Model that gets saved and fetched from the database. Represents a single row
    of a bank csv archive."""

    id: Annotated[int | None, Field(default=None, primary_key=True)]
    transaction_date: Annotated[date, Field(alias="Transaction Date")]
    amount: Annotated[Decimal, Field(alias="Amount")]
    description: Annotated[str, Field(alias="Description")]
    transaction_type: Annotated[str, Field(alias="Transaction Type")]
    file_name: Annotated[str, Field(foreign_key="consumedstatement.file_name")]

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
    file_name: Annotated[str, Field(alias="File Name", primary_key=True)]


class BankAccount(SQLModel, table=True):
    BankName: Annotated[str, Field(alias="Bank Name", primary_key=True)]


class MonthlyRecurring(SQLModel, table=True):
    id: Annotated[int | None, Field(default=None, primary_key=True)]
    day_of_month: Annotated[int, Field(alias="DayOfMonth")]
    amount: Annotated[Decimal, Field(alias="Amount")]
    last_payment_id: Annotated[int, Field(alias="Last Payment",
                                             foreign_key="bankentry.id")]


class UserProfile(BaseModel):
    id: Annotated[int | None, Field(default=None, primary_key=True)]
    salary: float
