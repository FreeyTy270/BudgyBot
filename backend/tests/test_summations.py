import logging
import calendar
from math import isclose
from pathlib import Path

import pytest
from sqlmodel import select, Session
from sqlmodel import extract

from budgybot.records_analysis import summations as sums
from budgybot import persistent_models as pms

cwd = Path(__file__).parent


@pytest.fixture
def add_data(tst_session, bank_account):
    tst_session.add(bank_account)
    if len(tst_session.exec(select(pms.Transaction.id)).all()) == 0:
        unread_data = bank_account.find_records()
        bank_account.update(tst_session, unread_data)


def get_monthly_total_raw(session: Session, moi: int, yoi: int) -> float:
    select_stmt = (
        select(pms.Transaction.amount)
        .filter(extract("year", pms.Transaction.transaction_date) == yoi)
        .filter(extract("month", pms.Transaction.transaction_date) == moi)
    )
    big_sum = session.exec(select_stmt).all()
    big_sum = sum(big_sum)
    return big_sum


def test_monthly_total(caplog, tst_session, add_data):
    log = logging.getLogger("test-monthly-total")
    years = [2023, 2024, 2025]
    the_sums = list()
    for year in years:
        for i in range(1, 13):
            ret_raw = get_monthly_total_raw(tst_session, i, year)
            ret = sums.calc_monthly_total(tst_session, i, year)
            if ret is not None:
                amt = f"{ret:.2f}"
            else:
                if ret_raw == 0:
                    ret_raw = None
                amt = ret

            the_sums.append((ret, ret_raw))
            log.info(f"Monthly total for {calendar.month_name[i]} {year}: {amt}")
    comps = []

    for fnc, raw in the_sums:
        if fnc and raw is not None:
            comps.append(isclose(fnc, raw, abs_tol=10**-3))
        else:
            comps.append(fnc == raw)
    assert all(comps)


def test_yearly_total(caplog, tst_session, add_data):
    log = logging.getLogger("test-yearly-total")
    years = [2023, 2024, 2025]
    the_sums = list()

    for year in years:
        ret_raw = 0
        for i in range(1, 13):
            if not (retrnd := get_monthly_total_raw(tst_session, i, year)):
                retrnd = 0
            ret_raw += retrnd

        ret = sums.calc_yearly_total(tst_session, year)

        if ret is not None:
            amt = f"{ret:.2f}"
        else:
            if ret_raw == 0:
                ret_raw = None
            amt = ret

        the_sums.append((ret, ret_raw))
        log.info(f"Total Revenue for {year}: {amt}")

    comps = []
    for fnc, raw in the_sums:
        if fnc and raw is not None:
            comps.append(isclose(fnc, raw, abs_tol=10**-3))
        else:
            comps.append(fnc == raw)
    assert all(comps)


def test_calc_credit_totals(caplog, tst_session, add_data):
    log = logging.getLogger("test-credit-total")
    assert True
