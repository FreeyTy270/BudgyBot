"""Defines the dataclass models (Pydantic) for Discover banking statements"""

from decimal import Decimal
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from budgybot.statement_models.abc import AbstractEntry
from budgybot.records_models import BankEntry
from budgybot.utils.helper_enums import DiscoverCreditCategory


class DiscoverCreditEntry(BaseModel, AbstractEntry):
    transaction_date: Annotated[datetime, Field(alias="Trans. Date")]
    posting_date: Annotated[datetime, Field(alias="Post Date")]
    description: Annotated[str, Field(alias="Description")]
    amount = Annotated[Decimal, Field(alias="Amount")]
    category: Annotated[DiscoverCreditCategory, Field(alias="Category")]

    @field_validator("posting_date", "transaction_date", mode="before")
    @classmethod
    def date_validator(cls, tx_date):
        if not isinstance(tx_date, datetime):
            tx_date = datetime.strptime(tx_date, "%m/%d/%Y")

        return tx_date

    def map_to_bank_entry(self) -> BankEntry:
        just_the_bits = self.model_dump(
            exclude={
                "check_num",
                "balance",
            }
        )

        return BankEntry(**just_the_bits)
