from decimal import Decimal
from typing_extensions import Annotated
from datetime import datetime

from sqlmodel import SQLModel, Field


class BankEntry(SQLModel, table=True):
    """Model that gets saved and fetched from the database. Represents a singls row
    of a bank csv archive."""
    id: Annotated[int | None, Field(default=None, primary_key=True)]
    transaction_date: Annotated[datetime, Field(alias="Transaction Date")]
    amount: Annotated[Decimal, Field(alias="Amount")]
    description: Annotated[str, Field(alias="Description")]
    transaction_type: Annotated[str, Field(alias="Transaction Type")]


class ConsumedStatements(SQLModel, table=True):
    id: Annotated[int | None, Field(default=None, primary_key=True)]
    file_name: Annotated[str, Field(alias="File Name")]
