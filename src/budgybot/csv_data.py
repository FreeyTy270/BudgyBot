import logging
from csv import DictReader
from pathlib import Path

from sqlmodel import Session, select

from budgybot.records_keeper import RecordsKeeper
from budgybot.records_models import BankEntry, ConsumedStatements
from budgybot.statement_models import ChaseCheckingEntry, ChaseCreditEntry
from budgybot.statement_models.abc import AbstractEntry
from budgybot.statement_models.discover import DiscoverCreditEntry
from pydantic_core._pydantic_core import ValidationError

log = logging.getLogger(__name__)
archives = Path(__file__).parent.parent / "bank_exports"


def find_data(keeper: RecordsKeeper) -> list[Path]:
    new_archives = list()
    all_archives = archives.glob("*.csv", case_sensitive=False)
    with Session() as session:
        files = session.exec(select(ConsumedStatements)).all()

    for file in files:
        if file not in all_archives:
            new_archives.append(file)

    return new_archives


def consume_file(file: Path) -> list[AbstractEntry]:
    """Reads data in from a csv file located at the Path specified by ``file``. Also
    updates the data held in the consumed file db.

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
                new_entry = entrytype(**row)
                csv_consumed.append(new_entry)
            except ValidationError as e:
                log.error(f"Object {entrytype} is not complete or properly formatted")


    return csv_consumed
