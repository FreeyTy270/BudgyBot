from datetime import datetime

from sqlalchemy import Engine, func
from sqlmodel import select, extract

from budgybot import records
from budgybot.records_models import BankEntry


def calc_monthly_total(
    engine: Engine, month_of_interest: int, year_of_interest: int
) -> float:
    current_year = datetime.now().year
    select_stmt = (
        select(func.sum(BankEntry.amount))
        .filter(extract("month", BankEntry.transaction_date) == month_of_interest)
        .filter(extract("year", BankEntry.transaction_date) == current_year)
    )

    big_sum = records.fetch(engine, select_stmt)[0]

    return big_sum
