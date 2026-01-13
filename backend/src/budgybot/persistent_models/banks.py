import logging
from csv import DictReader
from datetime import date
from pathlib import Path
from functools import cached_property
from typing import Optional

from sqlalchemy import Column
from pydantic import computed_field, ValidationError
from sqlmodel import SQLModel, Field, Relationship, Session

import budgybot.entry_types as etypes
from budgybot.utils import PathType, AccountType

from budgybot.persistent_models.transactions import (
    Transaction,
    ConsumedStatement,
    TransactionPublic,
)

log = logging.getLogger("budgybot")


class BankBase(SQLModel):
    name: str = Field(primary_key=True, nullable=False, unique=True)


class Bank(BankBase, table=True):
    accounts: list["BankAccount"] = Relationship(back_populates="bank")


class BankCreate(BankBase):
    pass


class BankPublic(BankBase):
    accounts: list["BankAccountPublic"]


class BankAccountBase(SQLModel):
    # model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(nullable=False, index=True)
    account_type: AccountType = Field(alias="Account Type", nullable=False)
    archive_dir: Path = Field(
        default=Path(__file__).parent.parent / "archive", sa_column=Column(PathType)
    )
    bank_name: str = Field(foreign_key="bank.name")


class BankAccount(BankAccountBase, table=True, arbitrary_types_allowed=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ### Relationships ###
    bank: Bank = Relationship(back_populates="accounts")
    statements: list[ConsumedStatement] = Relationship(back_populates="bank_account")
    transactions: list[Transaction] = Relationship(back_populates="bank_account")

    @computed_field
    @property
    def estimated_balance(self) -> float:
        return sum(self.transactions)

    @computed_field
    @cached_property
    def entry_format(self) -> type[etypes.StatementEntry]:
        """Uses Bank name and Account type to bind a handle to the entry type of this bank account."""
        if (
            self.bank.name.lower() == "chase"
            and self.account_type is AccountType.CHECKING
        ):
            fmt = etypes.ChaseCheckingEntry
        elif (
            self.bank.name.lower() == "chase"
            and self.account_type is AccountType.CREDIT
        ):
            fmt = etypes.ChaseCreditEntry
        elif (
            self.bank.name.lower() == "discover"
            and self.account_type is AccountType.CREDIT
        ):
            fmt = etypes.DiscoverCreditEntry

        return fmt

    def find_records(self) -> list[Path]:
        """Uses a glob pattern to find records in ``archive_dir``. Returns a list of
        file paths that are not in the list of ``previously_consumed`` records.

        :return: A list of file paths that have not already been consumed.
        """

        self_records = self.archive_dir.glob(f"{self.name}*.csv", case_sensitive=False)

        new_records = [
            record
            for record in self_records
            if record.stem not in [statement.file_name for statement in self.statements]
        ]

        return new_records

    def consume_csv_record(self, file: Path) -> list[etypes.StatementEntry]:
        """Reads data in from a csv file located at the Path specified by ``file``. Also
        updates the data held in the consumed file db.

        :param file: Path to the csv file.
        :return: A list of Transaction objects.
        """

        csv_consumed = list()

        with open(file, "r") as f:
            csv_reader = DictReader(f)
            for row in csv_reader:
                if None in row.keys():
                    row.pop(None)

                try:
                    row["file_name"] = file.stem
                    new_entry = self.entry_format(**row)
                    csv_consumed.append(new_entry)
                except ValidationError as e:
                    log.error(
                        f"Object {self.entry_format} is not complete or properly "
                        f"formatted\n{e}"
                    )
                    raise
        file_modified_date = date.fromtimestamp(file.stat().st_mtime)

        self.statements.append(
            ConsumedStatement(
                file_name=file.stem, report_date=file_modified_date, bank_account=self
            )
        )

        return csv_consumed

    def update(self, session: Session, list_o_records: list[Path]) -> None:
        """Loops through a list of records (``list_o_records``) and consumes them into
        the db.
        :param session: Active session for interacting with the database.
        :param list_o_records: List of records to consume.
        """
        normalized_entries = list()
        for record in list_o_records:
            record_entries = self.consume_csv_record(record)
            for i, entry in enumerate(record_entries):
                new_bankentry = entry.map_to_bank_entry(self.name)
                if not new_bankentry.already_exists(session):
                    normalized_entries.append(new_bankentry)
        self.transactions.extend(
            sorted(normalized_entries, key=lambda e: e.transaction_date)
        )


class BankAccountPublic(BankAccountBase):
    id: int
    # estimated_balance: float | None = None


class BankAccountPublicWithTransactions(BankAccountPublic):
    transactions: list[TransactionPublic]


class BankAccountCreate(BankAccountBase):
    pass


class BankAccountUpdate(SQLModel):

    name: str | None
    account_type: AccountType | None
    archive_dir: Path | None
    bank_name: str | None
