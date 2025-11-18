import logging
import calendar
from pathlib import Path

import pytest
from sqlmodel import select
from sqlalchemy import Engine
from sqlmodel import extract

from budgybot import records
from budgybot import csv_records
from budgybot.records_analysis import summations as sums
from budgybot.persistent_models.transactions import Transaction, ConsumedStatement

cwd = Path(__file__).parent


@pytest.fixture(scope="module")
def add_data(create_db_engine):
    if len(records.fetch(create_db_engine, select(Transaction.id))) == 0:
        read_files = records.fetch(
            create_db_engine, select(ConsumedStatement.file_name)
        )
        unread_data = csv_records.find_records(cwd / "archives", read_files)
        csv_records.loop_and_consume(create_db_engine, unread_data)


def get_monthly_total_raw(engine: Engine, moi: int, yoi: int) -> float:
    select_stmt = (
        select(Transaction.amount)
        .filter(extract("year", Transaction.transaction_date) == yoi)
        .filter(extract("month", Transaction.transaction_date) == moi)
    )
    big_sum = records.fetch(engine, select_stmt)
    big_sum = sum(big_sum)
    return big_sum


def test_monthly_total(caplog, create_db_engine, add_data):
    log = logging.getLogger("test-monthly-total")
    years = [2023, 2024, 2025]
    the_sums = list()
    for year in years:
        for i in range(1, 13):
            ret_raw = get_monthly_total_raw(create_db_engine, i, year)
            ret = sums.calc_monthly_total(create_db_engine, i, year)
            if ret is not None:
                amt = f"{ret:.2f}"
            else:
                if ret_raw == 0:
                    ret_raw = None
                amt = ret

            the_sums.append((ret, ret_raw))
            log.info(f"Monthly total for {calendar.month_name[i]} {year}: {amt}")

    assert all([True if fnc == raw else False for fnc, raw in the_sums])


def test_yearly_total(caplog, create_db_engine, add_data):
    log = logging.getLogger("test-yearly-total")
    years = [2023, 2024, 2025]
    the_sums = list()

    for year in years:
        ret_raw = 0
        for i in range(1, 13):
            if not (retrnd := get_monthly_total_raw(create_db_engine, i, year)):
                retrnd = 0
            ret_raw += retrnd

        ret = sums.calc_yearly_total(create_db_engine, year)
        the_sums.append((ret, ret_raw))

        if ret is not None:
            amt = f"{ret:.2f}"
        else:
            if ret_raw == 0:
                ret_raw = None
            amt = ret

        log.info(f"Total Revenue for {year}: {amt}")

    assert all([True if fnc == raw else False for fnc, raw in the_sums])
