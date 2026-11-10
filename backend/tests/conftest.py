import os
import random
from pathlib import Path
from datetime import date

import pytest
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select

from budgybot import entry_types as etypes
from budgybot import persistent_models as pms
from budgybot.persistent_models import BankAccount
from budgybot.utils import helper_enums


load_dotenv(verbose=True)

CWD = Path(__file__).parent
DB_URL = os.getenv("TDATABASE_URL")
DB_NAME = os.getenv("TDATABASE_NAME")


@pytest.fixture(
    scope="session",
    autouse=True,
)
def reset_db():
    test_db = Path(DB_URL).resolve() / DB_NAME
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


@pytest.fixture(scope="session")
def seed_test_banks(db_engine) -> list[pms.Bank]:
    bank_names = ("Chase", "Discover")
    banks = list()
    for bname in bank_names:
        banks.append(pms.Bank(name=bname))

    return banks


@pytest.fixture(scope="session", autouse=True)
def seed_test_bank_accounts(db_engine, seed_test_banks):
    chase_accts = list()
    discover_accts = list()
    for bank in seed_test_banks:
        match bank.name.lower():
            case "chase":
                for acct_type in etypes.CHASE_ACCT_TYPES:
                    chase_accts.append(
                        pms.BankAccount(
                            name=f"chase_{acct_type}",
                            bank=bank,
                            account_type=acct_type,
                            archive_dir=Path(__file__).parent / "archives",
                        )
                    )
            case "discover":
                for acct_type in etypes.DISCOVER_ACCT_TYPES:
                    discover_accts.append(
                        pms.BankAccount(
                            name=f"discover_{acct_type}",
                            bank=bank,
                            account_type=acct_type,
                        )
                    )

    with Session(db_engine) as session:
        session.add_all(chase_accts)
        session.add_all(discover_accts)
        session.commit()


@pytest.fixture(scope="session", autouse=True)
def seed_test_transactions(db_engine):
    with Session(db_engine) as session:
        bank_accounts = session.exec(select(pms.BankAccount)).all()
        for bank_account in bank_accounts:
            match bank_account.entry_format:
                case etypes.ChaseCheckingEntry:
                    entry_enum = helper_enums.ChaseDebitEntryType
                case etypes.ChaseCreditEntry:
                    entry_enum = helper_enums.ChaseCreditEntryType
                case etypes.DiscoverCreditEntry:
                    entry_enum = helper_enums.DiscoverCreditCategory
            txs = list()
            for _ in range(100):
                tx_type = random.choice(entry_enum._member_names_)
                tx = pms.Transaction(
                    transaction_date=date(
                        year=2024,
                        month=random.randint(1, 12),
                        day=random.randint(1, 28),
                    ),
                    amount=random.randint(-100, 100) + _ / 7,
                    description=f"Test {bank_account} Tx {_}",
                    transaction_type=entry_enum[tx_type],
                    notes=None,
                    bank_account=bank_account,
                )
                txs.append(tx)
            txs.sort(key=lambda x: x.transaction_date, reverse=True)
            session.add_all(txs)
            session.commit()


@pytest.fixture(scope="function", name="tst_session")
def make_session(db_engine):
    with Session(db_engine) as session, session.begin():
        yield session


@pytest.fixture(scope="function", name="ba_fetch_all")
def fetch_bank_accounts(db_engine):
    with Session(db_engine) as session:
        bas = session.exec(select(pms.BankAccount)).all()
    return bas


@pytest.fixture(
    scope="function",
    name="bank_account",
    params=["chase_checking", "chase_credit", "discover_credit"],
)
def fetch_bank_account(db_engine, request):
    with Session(db_engine) as session:
        ba = session.exec(
            select(pms.BankAccount).where(BankAccount.name == request.param)
        ).one()

    return ba
