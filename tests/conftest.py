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
    saved_data_records = records.fetch(create_db_engine, select(ConsumedStatement.file_name))
    golden_record = saved_data_records[random.randint(0, len(saved_data_records) - 1)]
    golden_path = [*archives.glob(f"{golden_record}.csv", case_sensitive=False)][0]
    test_record = copy(golden_path, archives / f"golden_{golden_record}.csv")

    yield test_record

    test_record.unlink()




def pytest_generate_tests(metafunc):
    if "file" in metafunc.fixturenames:
        archives = cwd / "archives"
        metafunc.parametrize("file", archives.glob("*.csv", case_sensitive=False))