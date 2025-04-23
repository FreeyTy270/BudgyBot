"""This file defines the program interface to the sqlite database"""

import logging

from sqlmodel import SQLModel, Session

from budgybot.statement_models import ChaseCheckingEntry
from budgybot.records_models import BankEntry

log = logging.getLogger(__name__)

class RecordsKeeper:
    def __init__(self, engine):
        self.engine = engine

    def add_single(self, item: BankEntry):
        with Session(self.engine) as session:
            log.debug(f"Adding {item} to records")
            session.add(item)
            session.commit()
            log.debug(f"{item} added and committed to records")
            session.refresh(item)

    def add_multi(self, items: list[BankEntry]):
        with Session(self.engine) as session:
            session.add_all(items)
            session.commit()
            log.debug("Multiple items added and committed to records")
            log.info("Multiple entries added")

    def remove(self, item: BankEntry):
        with Session(self.engine) as session:
            session.delete(item)
            session.commit()
            log.debug(f"{item} removed from records")

    def remove_multi(self, items: list[BankEntry]):
        with Session(self.engine) as session:
            for item in items:
                session.delete(item)

            session.commit()
            log.debug("Multiple items removed from records")
