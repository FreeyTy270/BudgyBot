import logging
from sqlalchemy import Engine, func
from sqlmodel import select, extract

from budgybot import records
from budgybot.records_models import BankEntry

log = logging.getLogger()


def calc_totals(engine: Engine, year_of_interest: int | None = None, month_of_interest: int | None = None, bank: str | None = None, credit_or_debit: str | None = None) -> float:
    select_stmt = (
        select(func.sum(BankEntry.amount))
    )
    if year_of_interest is not None:
        select_stmt.filter(extract("year", BankEntry.transaction_date) == year_of_interest)
    if month_of_interest is not None:
        select_stmt.filter(extract("month", BankEntry.transaction_date) == month_of_interest)
    if bank is not None:
        select_stmt.filter(bank in BankEntry.)
def calc_monthly_total(
    engine: Engine, month_of_interest: int, year_of_interest: int
) -> float:
    select_stmt = (
        select(func.sum(BankEntry.amount))
        .filter(extract("year", BankEntry.transaction_date) == year_of_interest)
        .filter(extract("month", BankEntry.transaction_date) == month_of_interest)
    )
    big_sum = records.fetch(engine, select_stmt)[0]

    return big_sum


def calc_yearly_total(engine: Engine, year_of_interest: int) -> float:
    select_stmt = select(func.sum(BankEntry.amount)).filter(
        extract("year", BankEntry.transaction_date) == year_of_interest
    )
    big_sum = records.fetch(engine, select_stmt)
    log.info(f"Raw return from fetch: {big_sum}")
    big_sum = big_sum[0]

    return big_sum
