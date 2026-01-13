import os
from shutil import copy
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select

from budgybot import persistent_models as pms, records
from budgybot.persistent_models import BankAccount
from budgybot.utils.helper_enums import AccountType


load_dotenv(verbose=True)

CWD = Path(__file__).parent
DB_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("DATABASE_NAME")


@pytest.fixture(scope="session", autouse=True)
def reset_db():
    test_db = Path(DB_URL).resolve()
    if test_db.exists():
        test_db.unlink()

    return test_db


@pytest.fixture(scope="session", name="db_engine")
def create_db_engine(reset_db):
    sql_path = f"sqlite:///{str(reset_db)}"
    test_engine = create_engine(sql_path, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(test_engine)

    yield test_engine

    test_engine.dispose()


@pytest.fixture(scope="function", name="tst_session")
def make_session(db_engine):
    with Session(db_engine) as session, session.begin():
        yield session


@pytest.fixture(scope="session")
def establish_banks(db_engine):
    """Create banks for use in the tests"""
    chase_bank = pms.Bank(name="Chase")
    discover_bank = pms.Bank(name="Discover")

    banks = {"chase": chase_bank, "discover": discover_bank}
    with Session(db_engine) as session:
        session.add_all(banks.values())
        session.commit()
        session.refresh(chase_bank)
        session.refresh(discover_bank)

    return banks


accounts = [
    {"name": "Chase6568", "type": AccountType.CHECKING},
    {"name": "Chase1050", "type": AccountType.CREDIT},
    {"name": "Discover", "type": AccountType.CREDIT},
]


@pytest.fixture(name="each_bank_account", params=accounts)
def get_each_bank_account(tst_session, establish_banks, request):
    select_stmt = select(BankAccount).where(BankAccount.name == request.param["name"])
    if (ba := records.fetch_one(tst_session, select_stmt)) is None:
        ba = pms.BankAccount(
            name=request.param["name"],
            account_type=request.param["type"],
            archive_dir=CWD / "archives",
            bank=(
                establish_banks["chase"]
                if "Chase" in request.param["name"]
                else establish_banks["discover"]
            ),
        )
        tst_session.add(ba)

    return ba


@pytest.fixture(name="bank_account")
def get_bank_account(tst_session, establish_banks):
    select_stmt = select(BankAccount).where(BankAccount.name == accounts[0]["name"])
    if (ba := records.fetch_one(tst_session, select_stmt)) is None:
        ba = pms.BankAccount(
            name=accounts[0]["name"],
            account_type=accounts[0]["type"],
            archive_dir=CWD / "archives",
            bank=(
                establish_banks["chase"]
                if "Chase" in accounts[0]["name"]
                else establish_banks["discover"]
            ),
        )
        tst_session.add(ba)

    return ba


@pytest.fixture
def create_copy_csv_record():
    archives = CWD / "archives"

    def _create_copy_csv_record(golden_path):
        test_record = copy(golden_path, archives / f"golden_{golden_path.stem}.csv")
        return test_record

    yield _create_copy_csv_record

    test_record = [*archives.glob("golden_*.csv")][0]
    if test_record:
        test_record.unlink()


# def pytest_generate_tests(metafunc):
#     if "file" in metafunc.fixturenames:
#         archives = CWD / "archives"
#         metafunc.parametrize("file", archives.glob("*.csv", case_sensitive=False))
