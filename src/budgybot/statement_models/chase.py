"""Defines the dataclass models (Pydantic) for Chase banking statements"""

import re
from decimal import Decimal
from datetime import datetime, date
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, computed_field

from budgybot.statement_models.abc import AbstractStatementEntry
from budgybot.records_models import BankEntry
from budgybot.utils.helper_enums import (
    ChaseDebitEntryType,
    ChaseCreditEntryType,
    ChaseCreditCategory,
)


# noinspection PyNestedDecorators
class ChaseCheckingEntry(BaseModel, AbstractStatementEntry):
    """Pydantic model of a single row from a Chase Checking Account csv archive."""

    details: Annotated[str, Field(alias="Details")]
    posting_date: Annotated[date, Field(alias="Posting Date")]
    description: Annotated[str, Field(alias="Description")]
    amount: Annotated[Decimal, Field(alias="Amount")]
    transaction_type: Annotated[ChaseDebitEntryType, Field(alias="Type")]
    balance: Annotated[Decimal | None, Field(alias="Balance")]
    check_num: Annotated[int | None, Field(alias="Check or Slip #", default=None)]
    file_name: str

    @computed_field
    @property
    def transaction_date(self) -> date:
        return self.posting_date

    @field_validator("posting_date", mode="before")
    @classmethod
    def date_validator(cls, tx_date):
        """Converts string representation of date into formatted datetime object."""
        if not isinstance(tx_date, datetime):
            tx_date = datetime.strptime(tx_date, "%m/%d/%Y").date()

        return tx_date

    @field_validator("transaction_type", mode="before")
    @classmethod
    def transaction_type_validator(cls, transaction_type):
        """Converts string representation of type into CDET enum instance."""
        if not isinstance(transaction_type, ChaseDebitEntryType):

            transaction_type = ChaseDebitEntryType[transaction_type.upper()]

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

    @field_validator("check_num", mode="before")
    @classmethod
    def check_num_validator(cls, check_num):
        """Converts 'empty' strings into NoneType."""
        arbitrary_spaces = re.compile(r"\s*")
        if re.match(arbitrary_spaces, check_num):
            check_num = None

        return check_num

    def map_to_bank_entry(self) -> BankEntry:
        """Dumps the model into a dictionary form containing only the fields found in
        ``BankEntry`` object and then returns a BankEntry instance."""

        just_the_bits = self.model_dump(
            exclude={
                "check_num",
                "balance",
            }
        )

        just_the_bits["transaction_type"] = self.transaction_type.value

        return BankEntry(**just_the_bits)


# noinspection PyNestedDecorators
class ChaseCreditEntry(BaseModel, AbstractStatementEntry):
    """Pydantic model of a single row from a Chase Credit Card Account csv archive."""

    transaction_date: Annotated[datetime, Field(alias="Transaction Date")]
    transaction_type: Annotated[ChaseCreditEntryType, Field(alias="Type")]
    posting_date: Annotated[datetime, Field(alias="Post Date")]
    description: Annotated[str, Field(alias="Description")]
    category: Annotated[ChaseCreditCategory, Field(alias="Category")]
    amount: Annotated[Decimal, Field(alias="Amount")]
    memo: Annotated[str | None, Field(alias="Memo")]
    file_name: str

    @field_validator("category", mode="before")
    @classmethod
    def category_validator(cls, category):
        if not category:
            category = ChaseCreditCategory.UNDEFINED
        elif not isinstance(category, ChaseCreditCategory):
            modded_str = category.replace(" &","").replace(" ", "_").upper()
            category = ChaseCreditCategory[modded_str]

        return category

    @field_validator("transaction_type", mode="before")
    @classmethod
    def transaction_type_validator(cls, transaction_type):
        if not transaction_type:
            transaction_type = ChaseCreditEntryType.UNDEFINED
        elif not isinstance(transaction_type, ChaseCreditEntryType):
            transaction_type = ChaseCreditEntryType[transaction_type.upper()]

        return transaction_type

    @field_validator("transaction_date","posting_date" ,mode="before")
    @classmethod
    def date_validator(cls, tx_date):
        """Converts string representation of date into formatted datetime object."""
        if not isinstance(tx_date, datetime):
            tx_date = datetime.strptime(tx_date, "%m/%d/%Y")

        return tx_date

    def map_to_bank_entry(self) -> BankEntry:
        just_the_bits = self.model_dump(
            exclude={"posting_date", "category", "memo"}
        )

        just_the_bits["transaction_type"] = self.transaction_type.value

        return BankEntry(**just_the_bits)
