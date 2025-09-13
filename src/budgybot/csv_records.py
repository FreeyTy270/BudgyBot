import logging
from csv import DictReader
from pathlib import Path
from builtins import type

from sqlalchemy import Engine
from sqlmodel import Session, select, and_

from pydantic_core._pydantic_core import ValidationError

from budgybot import records
from budgybot.records_models import ConsumedStatement, BankEntry
from budgybot.statement_models import ChaseCheckingEntry, ChaseCreditEntry
from budgybot.statement_models.abc import AbstractStatementEntry
from budgybot.statement_models.discover import DiscoverCreditEntry

log = logging.getLogger()


def find_records(engine: Engine, archive_dir: Path) -> list[Path]:
    """Uses a glob pattern to find records in ``archive_dir``. Returns a list of
    file paths that have not already been consumed.

    :param engine: The SQLAlchemy engine to use to find records.
    :param archive_dir: The directory to search for records in.
    :return: A list of file paths that have not already been consumed.
    """

    with Session(engine) as session:
        records_consumed = session.exec(select(ConsumedStatement.file_name)).all()

    records_in_archive = archive_dir.glob("*.csv", case_sensitive=False)

    return [record for record in records_in_archive if record.stem not in
            records_consumed]


def check_entry_exists_in_record(engine: Engine, entry: BankEntry) -> bool:
    """Checks whether an entry exists in the database. Used to prevent entries being
    committed to the database multiple times."""

    exists = False
    fetched = None
    fetch_statement = select(BankEntry).where(and_(BankEntry.description ==
                                              entry.description,
                                              BankEntry.transaction_date ==
                                                   entry.transaction_date,
                                              BankEntry.amount == entry.amount))
    if entry.id is None:
        fetched = records.fetch_one(engine, fetch_statement)
    else:
        exists = True
        log.warning(f"Provided BankEntry has db id already: {entry.id}")

    if fetched is not None:
        exists = True

    return exists


def consume_csv_record(engine: Engine, file: Path) -> list[type[AbstractStatementEntry]]:
    """Reads data in from a csv file located at the Path specified by ``file``. Also
    updates the data held in the consumed file db.

    :param engine: SQLAlchemy engine instance
    :param file: Path to the csv file.
    :return: A list of BankEntry objects.
    """

    csv_consumed = list()
    entrytype = None

    if "Chase" in file.stem and "6568" in file.stem:
        entrytype = ChaseCheckingEntry
    elif "Chase" in file.stem and "1050" in file.stem:
        entrytype = ChaseCreditEntry
    elif "Discover" in file.stem:
        entrytype = DiscoverCreditEntry
    else:
        log.error("Bank account archive NOT supported!!")
        raise TypeError("Bank account archive NOT supported!!")

    with open(file, "r") as f:
        csv_reader = DictReader(f)
        for row in csv_reader:
            if None in row.keys():
                row.pop(None)

            try:
                row["file_name"] = file.stem
                new_entry = entrytype(**row)
                csv_consumed.append(new_entry)
            except ValidationError as e:
                log.error(f"Object {entrytype} is not complete or properly formatted\n{e}")
                raise

    file_consumed = ConsumedStatement(file_name=file.stem)
    records.add_single(engine, file_consumed)

    return csv_consumed

def loop_and_consume(engine, list_o_records: list[Path]) -> None:
    """Loops through a list of records (``list_o_records``) and consumes them into
    the db.
    :param engine: SQLAlchemy engine instance
    :param list_o_records: List of records to consume.
    """

    for record in list_o_records:
        record_entries = consume_csv_record(engine, record)
        for i, entry in enumerate(record_entries):
            new_bankentry = entry.map_to_bank_entry()
            if not check_entry_exists_in_record(engine, new_bankentry):
                record_entries[i] = new_bankentry

    records.add_multi(engine, sorted(record_entries, key=lambda e:
    e.transaction_date))

