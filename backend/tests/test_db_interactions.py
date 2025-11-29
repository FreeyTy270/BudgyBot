import logging
from pathlib import Path

import pytest



@pytest.mark.dependency(name="data_in_db")
def test_get_data_into_db(tst_session, each_bank_account):
    
    bank_files = each_bank_account.find_records()
    normalized_entries = []
    for record in bank_files:
        record_entries = each_bank_account.consume_csv_record(record)
        for i, entry in enumerate(record_entries):
            new_bankentry = entry.map_to_bank_entry(each_bank_account.account_name)
            if not new_bankentry.already_exists(tst_session):
                normalized_entries.append(new_bankentry)

    entry_copies = normalized_entries.copy()
    an_entry = normalized_entries.pop()

    tst_session.add_all(sorted(normalized_entries, key=lambda e:
    e.transaction_date))
    tst_session.add(an_entry)

    assert an_entry.description == entry_copies[-1].description
    assert normalized_entries[0].description == entry_copies[0].description


@pytest.mark.dependency(depends=["data_in_db"])
def test_data_not_read_twice(each_bank_account):
    archives = Path(__file__).parent / "archives"

    files_not_read = each_bank_account.find_records()

    assert len(files_not_read) == 0


@pytest.mark.dependency(depends=["data_in_db"])
def test_no_repeat_data_in_db(caplog, tst_session,
                              create_copy_csv_record, each_bank_account):
    log = logging.getLogger("no-repeats")
    
    file = each_bank_account.archive_dir / f"{each_bank_account.statements[0].file_name}.csv"
    copy_csv = create_copy_csv_record(file)
    incorrect_count = 0
    record_entries = each_bank_account.consume_csv_record(copy_csv)
    for i, entry in enumerate(record_entries):
        new_bankentry = entry.map_to_bank_entry(each_bank_account.account_name)
        if not new_bankentry.already_exists(tst_session):
            log.error(
                f"Entry Passed Check: {new_bankentry.description}, "
                f"{new_bankentry.transaction_date}, {new_bankentry.amount}"
            )
            incorrect_count += 1

    assert incorrect_count == 0
