from pathlib import Path

import pytest
from sqlmodel import Session, select

from budgybot.csv_data import consume_file
from budgybot.statement_models import ChaseCheckingEntry, ChaseCreditEntry


@pytest.mark.dependency()
def test_get_data_into_db(hire_scribe):
    in_here = Path(__file__).parent
    archives = Path(in_here, "bank_exports")
    an_entry = None
    test_entry = None
    csv_files = archives.glob("*.csv", case_sensitive=False)
    for file in csv_files:
        the_entries = consume_file(file)
        for i, entry in enumerate(the_entries):
            the_entries[i] = entry.map_to_bank_entry()

        entry_copies = the_entries.copy()
        an_entry = the_entries.pop()

        hire_scribe.add_multi(the_entries)
        hire_scribe.add_single(an_entry)

        assert an_entry.description == entry_copies[-1].description
        assert the_entries[0].description == entry_copies[0].description


@pytest.mark.dependency(depends=["test_get_data_into_db"])
def test_demolition_team(hire_scribe, buy_manufactured):

    hire_scribe.remove(buy_manufactured)

    with Session(hire_scribe.engine) as session:
        result = session.exec(
            select(Room).where(Room.name == buy_manufactured.name)
        ).one_or_none()

    assert not result
