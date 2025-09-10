import logging
from pathlib import Path

from sqlmodel import create_engine, SQLModel

from budgybot import records
from budgybot.csv_data import find_data, consume_file

log = logging.getLogger(__name__)

cwd = Path(__file__).parent


def main():
    sql_db = "sqlite:///budgybot.db"
    printing_press = create_engine(sql_db)
    SQLModel.metadata.create_all(bind=printing_press)

    unread_data = find_data(printing_press)

    for file in unread_data:
        x = consume_file(file)
        for i, entry in enumerate(x):
            x[i] = entry.map_to_bank_entry()

        records.add_multi(printing_press, sorted(x, key=lambda e: e.transaction_date))


if __name__ == "__main__":
    main()
