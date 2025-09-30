import logging
import calendar

import pytest
from sqlmodel import select

from budgybot import records
from budgybot import csv_records
from budgybot.records_analysis import summations as sums
from budgybot.records_models import BankEntry, ConsumedStatement

from .conftest import cwd


@pytest.fixture(scope="module")
def add_data(create_db_engine):
    if len(records.fetch(create_db_engine, select(BankEntry.id))) == 0:
        read_files = records.fetch(
            create_db_engine, select(ConsumedStatement.file_name)
        )
        unread_data = csv_records.find_records(cwd / "archives", read_files)
        csv_records.loop_and_consume(create_db_engine, unread_data)


def test_monthly_total(caplog, create_db_engine, add_data):
    log = logging.getLogger("test-monthly-total")
    for i in range(1, 13):
        ret = sums.calc_monthly_total(create_db_engine, i)

        log.info(f"Monthly total for {calendar.month_name[i]}: {ret}")
    assert True
