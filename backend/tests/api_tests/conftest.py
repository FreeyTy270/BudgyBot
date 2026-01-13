import random
from datetime import date
from pathlib import Path

import pytest
from fastapi import FastAPI

from sqlmodel import Session
from starlette.testclient import TestClient

from budgybot import persistent_models as pms
from budgybot.api.transactions import router as transactions_router
from budgybot.records import get_session
from budgybot.utils import AccountType, ChaseDebitEntryType


@pytest.fixture(scope="session")
def client(db_engine):
    """Create a TestClient with the transactions router and an overridden DB session."""
    app = FastAPI()

    def override_get_session():
        with Session(db_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    app.include_router(transactions_router)
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session", name="bank_account")
def seed_bank_and_account(db_engine) -> pms.BankAccount:
    """Create and persist a Bank and BankAccount for tests."""
    with Session(db_engine) as session:
        # Create bank if missing
        bank = session.get(pms.Bank, "Chase")
        if bank is None:
            bank = pms.Bank(name="Chase")

        ba = pms.BankAccount(
            name="ChaseTestAccount",
            account_type=AccountType.CHECKING,
            archive_dir=Path(__file__).parent / "archives",  # not used by these tests
            bank=bank,
        )
        session.add(ba)
        session.commit()
        session.refresh(ba)
    return ba


@pytest.fixture(scope="session", name="transactions")
def seed_transactions(
    db_engine, bank_account: pms.BankAccount
) -> list[pms.Transaction]:
    txs: list[pms.Transaction] = []
    with Session(db_engine) as session:
        for i in range(1, 20):
            tx_type = random.choices(ChaseDebitEntryType._member_names_)[0]
            tx = pms.Transaction(
                transaction_date=date(2024, 1, random.randint(1, 28)),
                amount=random.randint(-100, 100) + i / 7,
                description=f"Test Tx {i}",
                transaction_type=ChaseDebitEntryType[tx_type],
                notes=None,
                bank_account=bank_account,
            )
            txs.append(tx)
        session.add_all(txs)
        session.commit()
        session.refresh(bank_account)
        txs = [tx for tx in txs if tx.id is not None]  ## Access all txs to ensure
        # they are not expired
    return txs
