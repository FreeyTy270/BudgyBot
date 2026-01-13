
def test_get_bank_accounts_all(client, db_engine):
    resp_all = client.get("/bankaccounts/")
    assert resp_all.status_code == 200
    assert resp_all.json == []
