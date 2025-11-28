"""This file defines the program interface to the sqlite database"""

import logging
from typing import Sequence, TypeVar

import sqlalchemy.exc
from sqlalchemy import Select
from sqlmodel import SQLModel, Session

_T = TypeVar("_T")
log = logging.getLogger()


def add_single(session: Session, item: type[SQLModel]) -> None:
    """Adds a single item to the database."""

    log.debug(f"Adding {type(item)} to records")
    session.add(item)

def add_multi(session: Session, items: list[type[SQLModel]]):
    """Adds multiple items to the database."""

    session.add_all(items)
    log.info(f"{len(items)} {type(items[0])} committed to records")

def remove(session: Session, item: type[SQLModel]):
    """Removes a single item from the database."""

    session.delete(item)
    log.debug(f"{type(item)} removed from records")

def remove_multi(session: Session, items: list[type[SQLModel]]):
    """Removes multiple items from the database."""
    for item in items:
        session.delete(item)
    log.debug(f"{len(items)} {type(items[0])} removed from records")


def fetch(session: Session, select_stmt: Select, size: int = 0) -> Sequence[_T]:
    """Fetches ``size`` records from the database. If ``size`` is left at ``0`` the
    function will return all records.

        :param session: The active db session to use.
        :param select_stmt: The select statement to execute.
        :param size: The number of records to fetch. Defaults to 0.
        :returns: A list of records.
    """

    records_result = session.exec(select_stmt)
    if size > 0:
        records = records_result.fetchmany(size=size)
    else:
        records = records_result.fetchall()

    return records

def fetch_one(session: Session, select_stmt: Select, okay_if_none: bool = True) -> _T:
    """Fetches a single record from the database.

        :param session: The active db session to use.
        :param select_stmt: The select statement to execute.
        :param okay_if_none: If ``True``, fetches using ``one_or_none()`` allowing for
        the fetch to return ``None`` without throwing an exception. Defaults to ``True``.
        :return: The fetched record or ``None``.
    """
    record = None

    try:
        if okay_if_none:
            record = session.exec(select_stmt).one_or_none()
        else:
            record = session.exec(select_stmt).one()
    except sqlalchemy.exc.MultipleResultsFound:
        num_records = len(session.exec(select_stmt).all())
        log.warning(f"{num_records} records found where 1 was expected")
    except sqlalchemy.exc.NoResultFound:
        log.error("No records were found where 1 was needed")
        ## TODO: Create custom exception behavior when necessary

    return record
