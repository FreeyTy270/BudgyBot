"""This file defines the program interface to the sqlite database"""

import logging

from sqlalchemy import Engine
from sqlmodel import SQLModel, Session

log = logging.getLogger(__name__)


def add_single(engine: Engine, item: type[SQLModel]) -> None:
    """Adds a single item to the database."""
    with Session(engine) as session:
        log.debug(f"Adding {item} to records")
        session.add(item)
        session.commit()
        log.debug(f"{item} added and committed to records")
        session.refresh(item)

def add_multi(engine: Engine, items: list[type[SQLModel]]):
    """Adds multiple items to the database."""
    with Session(engine) as session:
        session.add_all(items)
        session.commit()
        log.debug("Multiple items added and committed to records")
        log.info("Multiple entries added")
        for item in items:
            session.refresh(item)

def remove(engine: Engine, item: type[SQLModel]):
    """Removes a single item from the database."""
    with Session(engine) as session:
        session.delete(item)
        session.commit()
        log.debug(f"{item} removed from records")

def remove_multi(engine: Engine, items: list[type[SQLModel]]):
    """Removes multiple items from the database."""
    with Session(engine) as session:
        for item in items:
            session.delete(item)

        session.commit()
        log.debug("Multiple items removed from records")
