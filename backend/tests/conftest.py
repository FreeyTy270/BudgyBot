import os
import random
from datetime import date
from os import tcsetpgrp
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select

from budgybot import entry_types as etypes
from budgybot import persistent_models as pms
from budgybot.utils.helper_enums import AccountType


load_dotenv(verbose=True)

CWD = Path(__file__).parent
DB_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("DATABASE_NAME")


@pytest.fixture(scope="session", autouse=True)
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


@pytest.fixture(scope="session")
def seed_test_bank_accounts(db_engine, seed_test_banks):
    chase_accts = list()
    discover_accts = list()
    for bank in seed_test_banks:
        match bank.name:
            case "chase":
                for acct_type in etypes.CHASE_ACCT_TYPES:
                    chase_accts.append(
                        pms.BankAccount(
                            name=f"chase_{acct_type}",
                            bank=bank,
                        )
                    )
            case "discover":
                for acct_type in etypes.DISCOVER_ACCT_TYPES:
                    discover_accts.append(
                        pms.BankAccount(
                            name=f"discover_{acct_type}",
                            bank=bank,
                        )
                    )

    with Session(db_engine) as session:
        session.add_all(chase_accts)
        session.add_all(discover_accts)
        session.commit()


@pytest.fixture(scope="session")
def seed_test_transactions(db_engine, seed_test_bank_accounts):
    with Session(db_engine) as session:
        bank_accounts = session.exec(select(pms.BankAccount)).all()
        for bank_account in bank_accounts:
            txs = list()
            for _ in range(100):
                tx_type = random.choice(bank_account.entry_format._member_names_)
                tx = pms.Transaction(
                    transaction_date=date(
                        year=2024,
                        month=random.randint(1, 12),
                        day=random.randint(1, 28),
                    ),
                    amount=random.randint(-100, 100) + i / 7,
                    description=f"Test {bank_account} Tx {i}",
                    transaction_type=bank_account.entry_format[tx_type],
                    notes=None,
                    bank_account=bank_account,
                )
                txs.append(tx)
            session.add_all(txs)
            session.commit()


@pytest.fixture(scope="function", name="tst_session")
def make_session(db_engine):
    with Session(db_engine) as session, session.begin():
        yield session
