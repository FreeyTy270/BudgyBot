from __future__ import annotations
import logging
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship, select, and_, Session

if TYPE_CHECKING:
    from budgybot.persistent_models.banks import BankAccount, BankAccountPublic


log = logging.getLogger("budgybot")


class TransactionBase(SQLModel):
    """Base transaction model, NON-TABLE"""

    transaction_date: date = Field(index=True, alias="Transaction Date")
    amount: Decimal = Field(alias="Amount")
    description: str = Field(alias="Description")
    transaction_type: str = Field(alias="Transaction Type")
    notes: Optional[str] = Field(default=None, title="Notes")

    bank_account_name: str = Field(foreign_key="bankaccount.name")

    """Credit for the __add__ and __radd__ implementations goes to this comment https://discuss.python.org/t/how-to-overload-add-method-in-a-self-made-class-to-sum-multiple-objects-of-the-class/40543/4"""

    def __add__(self, other: Transaction | int | float) -> int | float | Decimal:
        if isinstance(other, Transaction):
            return self.amount + other.amount
        elif isinstance(other, int) or isinstance(other, float):
            return self.amount + other
        else:
            raise TypeError("Unsupported operand type(s) for +")

    def __radd__(self, other: Transaction | int | float):
        return self.__add__(other)


class Transaction(TransactionBase, table=True):
    """Model that gets saved and fetched from the database. Represents a single row
    of a bank csv archive."""

    id: Optional[int] = Field(default=None, primary_key=True)
    bank_account: BankAccount = Relationship(back_populates="transactions")

    # TODO: Figure out why this is not working
    # @computed_field
    # @property
    # def transaction_id(self) -> int | None:
    #     tx_id = None
    #     if "ID:" in self.description:
    #         desc_split = self.description.split("ID:")
    #         self.description = desc_split[0]
    #         tx_id = int(desc_split[1])
    #     return tx_id

    def already_exists(self, session: Session) -> bool:
        """Checks whether an entry exists in the database. Used to prevent entries being
        committed to the database multiple times."""

        exists = False
        fetch_statement = select(Transaction).where(
            and_(
                Transaction.description == self.description,
                Transaction.transaction_date == self.transaction_date,
                Transaction.amount == self.amount,
            )
        )
        if self.id is None:
            """This fetch was changed from .one() to .all() after discovering an edge
            case of having multiple valid transactions sharing a date, description,
            and amount. Program will allow multiple 'identical' transactions
            when loaded in from the same file by virtue of all entries within a csv file being added to db at the same time
            """
            if session.exec(fetch_statement).all():
                exists = True
        else:
            exists = True
            log.warning(f"Provided Transaction has db id already: {self.id}")

        return exists


class TransactionPublic(TransactionBase):
    id: int


class TransactionPublicWithAccount(TransactionPublic):
    bank_account: BankAccountPublic


class ConsumedStatement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    file_name: str = Field(alias="File Name")
    report_date: date = Field(alias="Report Date")
    bank_account_name: str = Field(foreign_key="bankaccount.name")
    bank_account: BankAccount = Relationship(back_populates="statements")
