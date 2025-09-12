"""Defines the dataclass models (Pydantic) for Discover banking statements"""

from decimal import Decimal
from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from budgybot.statement_models.abc import AbstractStatementEntry
from budgybot.records_models import BankEntry
from budgybot.utils.helper_enums import DiscoverCreditCategory


class DiscoverCreditEntry(BaseModel, AbstractStatementEntry):
    """Pydantic model of a single row from a Discover Credit Card Account csv archive."""

    transaction_date: Annotated[date, Field(alias="Trans. Date")]
    posting_date: Annotated[date, Field(alias="Post Date")]
    description: Annotated[str, Field(alias="Description")]
    amount: Annotated[Decimal, Field(alias="Amount")]
    category: Annotated[DiscoverCreditCategory, Field(alias="Category")]
    file_name: str

    @field_validator("posting_date", "transaction_date", mode="before")
    @classmethod
    def date_validator(cls, tx_date):
        """Converts string representation of date into formatted datetime object."""
        if not isinstance(tx_date, date):
            tx_date = datetime.strptime(tx_date, "%m/%d/%Y").date()

        return tx_date

    @field_validator("category", mode="before")
    @classmethod
    def category_validator(cls, category):
        if not category:
            category = DiscoverCreditCategory.UNDEFINED
        elif not isinstance(category, DiscoverCreditCategory):
            if "Payments" in category:
                category = "payments"
            category = DiscoverCreditCategory[category.upper()]

        return category

    def map_to_bank_entry(self) -> BankEntry:
        """
        Maps the current model's data to a `BankEntry` instance while excluding
        specific fields like `check_num` and `balance`.

        :raises TypeError: If the dictionary passed to the `BankEntry` constructor
            does not match the expected parameters.
        :return: A new `BankEntry` instance created from the current model's data.
        :rtype: BankEntry
        """
        just_the_bits = self.model_dump(
            exclude={
                "check_num",
                "balance",
            }
        )

        just_the_bits["transaction_type"] = self.category.value

        return BankEntry(**just_the_bits)
