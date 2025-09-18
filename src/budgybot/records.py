"""This file defines the program interface to the sqlite database"""

import logging
from typing import Sequence

import sqlalchemy.exc
from sqlalchemy import Engine, Select
from sqlmodel import SQLModel, Session
from sqlmodel.sql._expression_select_cls import _T

log = logging.getLogger()


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

def fetch(engine: Engine, select_stmt: Select, size: int = 0) -> Sequence[_T]:
    """Fetches ``size`` records from the database. If ``size`` is left at ``0`` the
    function will return all records.

        :param engine: The database engine to use.
        :param select_stmt: The select statement to execute.
        :param size: The number of records to fetch. Defaults to 0.
        :returns: A list of records.
    """

    with Session(engine) as session:
        records_result = session.exec(select_stmt)
        if size > 0:
            records = records_result.fetchmany(size=size)
        else:
            records = records_result.fetchall()

    return records

def fetch_one(engine: Engine, select_stmt: Select, okay_if_none: bool = True) -> _T:
    """Fetches a single record from the database.

        :param engine: The database engine to use.
        :param select_stmt: The select statement to execute.
        :param okay_if_none: If ``True``, fetches using ``one_or_none()`` allowing for
        the fetch to return ``None`` without throwing an exception. Defaults to ``True``.
        :return: The fetched record or ``None``.
    """
    record = None

    with Session(engine) as session:
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
