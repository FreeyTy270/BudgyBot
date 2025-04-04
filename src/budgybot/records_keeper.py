"""This file defines the program interface to the sqlite database"""

from sqlmodel import SQLModel, Session

from budgybot.statement_models import ChaseCheckingEntry
from budgybot.records_models import BankEntry


class RecordsKeeper:
    def __init__(self, engine):
        self.engine = engine

    def add_single(self, item: BankEntry):
        with Session(self.engine) as session:
            session.add(item)
            session.commit()
            session.refresh(item)

    def add_multi(self, items: list[BankEntry]):
        with Session(self.engine) as session:
            session.add_all(items)
            session.commit()

    def remove(self, item: BankEntry):
        with Session(self.engine) as session:
            session.delete(item)
            session.commit()

    def remove_multi(self, items: list[BankEntry]):
        with Session(self.engine) as session:
            for item in items:
                session.delete(item)

            session.commit()

