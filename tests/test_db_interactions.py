import pytest

from budgybot import records
from budgybot.csv_data import consume_file, find_data
from tests.conftest import create_db_engine


@pytest.mark.dependency()
def test_get_data_into_db(create_db_engine, file):

    the_entries = consume_file(create_db_engine, file)
    for i, entry in enumerate(the_entries):
        the_entries[i] = entry.map_to_bank_entry()

    entry_copies = the_entries.copy()
    an_entry = the_entries.pop()

    records.add_multi(create_db_engine, the_entries)
    records.add_single(create_db_engine, an_entry)

    assert an_entry.description == entry_copies[-1].description
    assert the_entries[0].description == entry_copies[0].description


# @pytest.mark.dependency(depends=["test_get_data_into_db"])
# def test_demolition_team(hire_scribe, buy_manufactured):
#
#     hire_scribe.remove(buy_manufactured)
#
#     with Session(hire_scribe.engine) as session:
#         result = session.exec(
#             select(Room).where(Room.name == buy_manufactured.name)
#         ).one_or_none()
#
#     assert not result
