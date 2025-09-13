from pathlib import Path

import pytest

from budgybot import records
from budgybot.csv_records import (
    consume_csv_record,
    find_records,
    loop_and_consume,
    check_entry_exists_in_record,
)


@pytest.mark.dependency()
def test_get_data_into_db(create_db_engine, file):

    the_entries = consume_csv_record(create_db_engine, file)
    for i, entry in enumerate(the_entries):
        the_entries[i] = entry.map_to_bank_entry()

    entry_copies = the_entries.copy()
    an_entry = the_entries.pop()

    records.add_multi(create_db_engine, the_entries)
    records.add_single(create_db_engine, an_entry)

    assert an_entry.description == entry_copies[-1].description
    assert the_entries[0].description == entry_copies[0].description


@pytest.mark.dependency(depends=["test_get_data_into_db"])
def test_data_not_read_twice(create_db_engine):
    archives = Path(__file__).parent / "archives"
    files_not_read = find_records(create_db_engine, archives)

    assert len(files_not_read) == 0


@pytest.mark.dependency(depends=["test_get_data_into_db"])
def test_no_repeat_data_in_db(create_db_engine, create_copy_csv_record):
    incorrect_count = 0
    record_entries = consume_csv_record(create_db_engine, create_copy_csv_record)
    for i, entry in enumerate(record_entries):
        new_bankentry = entry.map_to_bank_entry()
        if not check_entry_exists_in_record(create_db_engine, new_bankentry):
            incorrect_count += 1

    assert incorrect_count == 0
