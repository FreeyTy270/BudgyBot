"""This file defines the program interface to the sqlite database"""

from sqlmodel import SQLModel

from budgybot.statement_models.chase import ChaseCheckingEntry



def create_records_keeper(db_engine) -> None:

    SQLModel.metadata.create_all(bind=db_engine)

