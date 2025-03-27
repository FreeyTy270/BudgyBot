
from decimal import Decimal
from typing_extensions import Annotated

from sqlalchemy import String, DateTime
from sqlmodel import SQLModel, Field

class BankEntry(SQLModel, table=True):
    id: Annotated[int | None, Field(default=None, primary_key=True)]
    posting_date: Annotated[DateTime, Field(alias="Posting Date")]
    amount: Annotated[Decimal, Field(alias="Amount")]
    description: Annotated[str, Field(alias="Description")]
    transaction_type: Annotated[str, Field(alias="Transaction Type")]