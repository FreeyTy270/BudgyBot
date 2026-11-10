def test_get_bank_accounts_all(client, db_engine):
    resp_all = client.get("/bank-accounts/")
    assert resp_all.status_code == 200
    assert len(resp_all.json()) == 3
