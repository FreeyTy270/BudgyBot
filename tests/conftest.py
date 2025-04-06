from pathlib import Path

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Session, create_engine

from budgybot.records_keeper import RecordsKeeper
from budgybot.statement_models import ChaseCheckingEntry, ChaseCreditEntry


@pytest.fixture(scope="session")
def reset_db():
    cwd = Path(__file__).parent
    test_db = Path(cwd, "test.db")
    if test_db.exists():
        test_db.unlink()


@pytest.fixture(scope="session")
def create_db_engine(reset_db):
    sql_path = "sqlite:///tests/test.db"
    test_engine = create_engine(sql_path)
    SQLModel.metadata.create_all(test_engine)

    yield test_engine


@pytest.fixture(scope="session")
def hire_scribe(create_db_engine):
    yield RecordsKeeper(create_db_engine)
