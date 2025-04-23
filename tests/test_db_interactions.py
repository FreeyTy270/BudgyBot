from pathlib import Path

import pytest
from sqlmodel import Session, select

from budgybot.csv_data import consume_file
from budgybot.statement_models import ChaseCheckingEntry, ChaseCreditEntry

@pytest.mark.dependency()
def test_get_data_into_db(hire_scribe):
    in_here = Path(__file__).parent
    archives = Path(in_here, "archives")
    for file in archives.glob("*.csv"):
        the_entries = consume_file(file)
        for entry in the_entries:
            entry.map_to_bank_entry()



@pytest.mark.dependency(depends=["test_get_data_into_db"])
def test_demolition_team(hire_scribe, buy_manufactured):

    hire_scribe.remove(buy_manufactured)

    with Session(hire_scribe.engine) as session:
        result = session.exec(
            select(Room).where(Room.name == buy_manufactured.name)
        ).one_or_none()

    assert not result
