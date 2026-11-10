from random import randint

import pytest


def test_get_transactions_all(client, all_txs):

    # All
    resp_all = client.get("/transactions/")
    assert resp_all.status_code == 200
    body_all = resp_all.json()
    assert isinstance(body_all, list)
    assert len(body_all) >= 5


def test_get_all_bank_account_transactions(client, bank_account, all_txs):
    resp_all = client.get(f"/transactions/?ba_id={bank_account.id}")
    assert resp_all.status_code == 200
    body_all = resp_all.json()
    assert isinstance(body_all, list)
    assert all(
        bank_account.name == fetched["bank_account_name"] for fetched in body_all
    )


@pytest.mark.parametrize("offset", [0, 3, 6])
def test_get_transactions_pagination(client, all_txs, offset):
    # Limit and offset
    limit = 3
    resp_page = client.get(f"/transactions/?limit={limit}&offset={offset}")
    assert resp_page.status_code == 200
    body_page = resp_page.json()
    assert len(body_page) == limit

    # Verify one of our known descriptions appears somewhere in results
    assert body_page[1]["description"] == all_txs[offset + 1]["description"]


def test_get_single_transaction_success(client, bank_account, all_txs):
    tx_id = randint(1, len(all_txs))
    tx = all_txs[tx_id - 1]

    # Success
    resp_ok = client.get(f"/transactions/{tx_id}")
    assert resp_ok.status_code == 200
    data = resp_ok.json()
    assert data["id"] == tx["id"]
    assert data["description"] == tx["description"]
    # bank_account object should be present due to response model
    assert isinstance(data.get("bank_account"), dict)


def test_get_single_transaction_404(client):

    resp_404 = client.get("/transactions/999999")
    assert resp_404.status_code == 404
    assert resp_404.json()["detail"] == "Transaction not found"


def test_delete_transaction_success_then_404(client, all_txs):
    tx_id = randint(0, len(all_txs) - 1)
    # delete
    resp_del = client.delete(f"/transactions/{tx_id}")
    assert resp_del.status_code == 200
    assert resp_del.json() == {"success": True}

    # ensure it is gone
    resp_get = client.get(f"/transactions/{tx_id}")
    assert resp_get.status_code == 404

    # delete again should 404
    resp_del_missing = client.delete(f"/transactions/{tx_id}")
    assert resp_del_missing.status_code == 404
    assert resp_del_missing.json()["detail"] == "Transaction not found"
