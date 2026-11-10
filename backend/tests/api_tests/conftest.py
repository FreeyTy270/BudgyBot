import pytest
from fastapi import FastAPI

from sqlmodel import Session
from starlette.testclient import TestClient

from budgybot.api.transactions import router as transactions_router
from budgybot.api.bankaccount import router as bank_account_router
from budgybot.records import get_session


@pytest.fixture(scope="session")
def client(db_engine):
    """Create a TestClient with the transaction's router and an overridden DB session."""
    app = FastAPI()

    def override_get_session():
        with Session(db_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    app.include_router(transactions_router)
    app.include_router(bank_account_router)
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function", name="all_txs")
def fetch_transactions(client):
    response = client.get("/transactions")
    assert response.status_code == 200
    return response.json()
