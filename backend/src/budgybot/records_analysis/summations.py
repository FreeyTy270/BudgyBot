import logging
from typing import Literal

from sqlalchemy import func
from sqlmodel import select, extract, Session

from budgybot import records
from budgybot.persistent_models import Transaction

log = logging.getLogger()


def calc_totals(
    session: Session,
    year_of_interest: int | None = None,
    month_of_interest: int | None = None,
    bank: str | None = None,
    credit_or_debit: Literal["CREDIT", "DEBIT"] | None = None,
) -> float:
    select_stmt = select(func.sum(Transaction.amount))
    if year_of_interest is not None and month_of_interest is None:
        select_stmt.filter(
            extract("year", Transaction.transaction_date) == year_of_interest
        )
    if month_of_interest is not None and year_of_interest is not None:
        select_stmt.filter(
            extract("month", Transaction.transaction_date) == month_of_interest
        )
    elif month_of_interest is not None and year_of_interest is None:
        raise ValueError("year_of_interest cannot be None when filtering by month")
    if bank is not None:
        select_stmt.filter(bank in Transaction.bank_account.bank)
    if credit_or_debit is not None:
        select_stmt.filter(credit_or_debit == Transaction.transaction_type)

    fetched = records.fetch(session, select_stmt)
    return fetched


def calc_monthly_total(
    session: Session, month_of_interest: int, year_of_interest: int
) -> float:
    select_stmt = (
        select(func.sum(Transaction.amount))
        .filter(extract("year", Transaction.transaction_date) == year_of_interest)
        .filter(extract("month", Transaction.transaction_date) == month_of_interest)
    )
    big_sum = records.fetch_one(session, select_stmt)

    return big_sum


def calc_yearly_total(session: Session, year_of_interest: int) -> float:
    select_stmt = select(func.sum(Transaction.amount)).filter(
        extract("year", Transaction.transaction_date) == year_of_interest
    )
    big_sum = records.fetch_one(session, select_stmt)
    log.info(f"Raw return from fetch: {big_sum}")

    return big_sum
