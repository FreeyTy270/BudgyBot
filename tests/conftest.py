import random
from shutil import copy
from pathlib import Path

import pytest
from sqlmodel import SQLModel, create_engine, select

from budgybot import records
from budgybot.records_models import ConsumedStatement


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


@pytest.fixture
def create_copy_csv_record(create_db_engine):
    archives = cwd / "archives"

    def _create_copy_csv_record(golden_path):
        test_record = copy(golden_path, archives / f"golden_{golden_path.stem}.csv")
        return test_record

    yield _create_copy_csv_record

    test_record = [*archives.glob(f"golden_*.csv")][0]
    if test_record:
        test_record.unlink()





def pytest_generate_tests(metafunc):
    if "file" in metafunc.fixturenames:
        archives = cwd / "archives"
        metafunc.parametrize("file", archives.glob("*.csv", case_sensitive=False))