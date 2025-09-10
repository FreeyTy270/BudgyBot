from pathlib import Path

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Session, create_engine

from budgybot import records
from budgybot.statement_models import ChaseCheckingEntry, ChaseCreditEntry


cwd = Path(__file__).parent

@pytest.fixture(scope="session")
def reset_db():
    test_db = Path(cwd, "test.db")
    if test_db.exists():
        test_db.unlink()

    return test_db


@pytest.fixture(scope="session")
def create_db_engine(reset_db):
    sql_path = f"sqlite:///{str(reset_db)}"
    test_engine = create_engine(sql_path)
    SQLModel.metadata.create_all(test_engine)

    yield test_engine

    test_engine.dispose()


def pytest_generate_tests(metafunc):
    if "file" in metafunc.fixturenames:
        archives = cwd / "archives"
        metafunc.parametrize("file", archives.glob("*.csv", case_sensitive=False))