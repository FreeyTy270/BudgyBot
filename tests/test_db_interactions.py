from sqlmodel import Session, select

from budgybot.csv_data import consume_file
from budgybot.statement_models import ChaseCheckingEntry, ChaseCreditEntry


def test_make_an_entry(hire_scribe):
    entry_list = consume_file()

    hire_scribe.add_single(house)

    with Session(hire_scribe.engine) as session:
        result = session.exec(select(Room)).one()

    assert result.name == "Test House"


def test_demolition_team(hire_scribe, buy_manufactured):

    hire_scribe.remove(buy_manufactured)

    with Session(hire_scribe.engine) as session:
        result = session.exec(
            select(Room).where(Room.name == buy_manufactured.name)
        ).one_or_none()

    assert not result
