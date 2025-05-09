"""Defines the dataclass models (Pydantic) for Chase banking statements"""

import re
from decimal import Decimal
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from budgybot.statement_models.abc import AbstractEntry
from budgybot.records_models import BankEntry
from budgybot.utils.helper_enums import (
    ChaseDebitEntryType,
    ChaseCreditEntryType,
    ChaseCreditCategory,
)


# noinspection PyNestedDecorators
class ChaseCheckingEntry(BaseModel, AbstractEntry):
    """Pydantic model of a single row from a Chase Checking Account csv archive."""

    details: Annotated[str, Field(alias="Details")]
    posting_date: Annotated[datetime, Field(alias="Posting Date", init_var=True)]
    transaction_date: Annotated[datetime, Field(alias="Transaction Date", init=False)]
    description: Annotated[str, Field(alias="Description")]
    amount: Annotated[Decimal, Field(alias="Amount")]
    transaction_type: Annotated[ChaseDebitEntryType, Field(alias="Type")]
    balance: Annotated[Decimal | None, Field(alias="Balance")]
    check_num: Annotated[int | None, Field(alias="Check or Slip #", default=None)]

    @field_validator("posting_date", "transaction_date", mode="before")
    @classmethod
    def date_validator(cls, tx_date):
        """Converts string representation of date into formatted datetime object."""
        if not isinstance(tx_date, datetime):
            tx_date = datetime.strptime(tx_date, "%m/%d/%Y")

        return tx_date

    @field_validator("transaction_type", mode="before")
    @classmethod
    def transaction_type_validator(cls, transaction_type):
        """Converts string representation of type into CDET enum instance."""
        if not isinstance(transaction_type, ChaseDebitEntryType):
            transaction_type = ChaseDebitEntryType[transaction_type]

        return transaction_type

    @field_validator("balance", mode="before")
    @classmethod
    def balance_validator(cls, balance):
        """Converts 'empty' strings into NoneType. This represents a transactions
        which has not yet been posted."""
        arbitrary_spaces = re.compile(r"\s+")
        if re.match(arbitrary_spaces, balance):
            balance = None

        return balance

    def model_post_init(self, posting_date: datetime):
        """Sets the transaction date as the posting date for an easier conversion to
        ``BankEntry`` object before saving to the db."""
        self.transaction_date = posting_date

    def map_to_bank_entry(self) -> BankEntry:
        """Dumps the model into a dictionary form containing only the fields found in
        ``BankEntry`` object and then returns a BankEntry instance."""
        just_the_bits = self.model_dump(
            exclude={
                "check_num",
                "balance",
            }
        )

        return BankEntry(**just_the_bits)


# noinspection PyNestedDecorators
class ChaseCreditEntry(BaseModel, AbstractEntry):
    """Pydantic model of a single row from a Chase Credit Card Account csv archive."""
    transaction_date: Annotated[datetime, Field(alias="Transaction Date")]
    transaction_type: Annotated[ChaseCreditEntryType, Field(alias="Type")]
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

    def map_to_bank_entry(self) -> BankEntry:
        just_the_bits = self.model_dump(
            exclude={"transaction_type", "posting_date", "category", "memo"}
        )

        return BankEntry(**just_the_bits)
