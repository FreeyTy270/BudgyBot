"""Defines the dataclass models (Pydantic) for Chase banking statements"""

import re
from decimal import Decimal
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from budgybot.utils.helper_enums import ChaseDebitEntryType, ChaseCreditEntryType, ChaseCreditCategory


class ChaseCheckingEntry(BaseModel):
    details: Annotated[str, Field(alias="Details")]
    posting_date: Annotated[datetime, Field(alias="Posting Date")]
    description: Annotated[str, Field(alias="Description")]
    amount: Annotated[Decimal, Field(alias="Amount")]
    transaction_type: Annotated[ChaseDebitEntryType, Field(alias="Type")]
    balance: Annotated[Decimal | None, Field(alias="Balance")]
    check_num: Annotated[int | None, Field(alias="Check  or Slip #", default=None)]

    @field_validator("posting_date", mode="before")
    @classmethod
    def posting_date_validator(cls, posting_date):
        if not isinstance(posting_date, datetime):
            posting_date = datetime.strptime(posting_date, "%m/%d/%Y")

        return posting_date

    @field_validator("transaction_type", mode="before")
    @classmethod
    def transaction_type_validator(cls, transaction_type):
        if not isinstance(transaction_type, ChaseDebitEntryType):
            transaction_type = ChaseDebitEntryType[transaction_type]

        return transaction_type

    @field_validator("balance", mode="before")
    @classmethod
    def balance_validator(cls, balance):
        arbitrary_spaces = re.compile(r"\s+")
        if re.match(arbitrary_spaces, balance):
            balance = None

        return balance


class ChaseCreditEntry(BaseModel):
    transaction_date: Annotated[datetime, Field(alias="Transaction Date")]
    posting_date: Annotated[datetime, Field(alias="Posting Date")]
    description: Annotated[str, Field(alias="Description")]
    category: Annotated[ChaseCreditCategory, Field(alias="Category")]
    amount: Annotated[Decimal, Field(alias="Amount")]
    memo: Annotated[str | None, Field(alias="Memo")]

    @field_validator("category", mode="before")
    @classmethod
    def category_validator(cls, category):
        if not category:
            category = ChaseCreditCategory.UNDEFINED

        return category
