import logging
from pathlib import Path

from sqlmodel import create_engine, SQLModel

from budgybot.csv_data import find_data, consume_file
from budgybot.records_keeper import RecordsKeeper

log = logging.getLogger(__name__)

cwd = Path(__file__).parent


def main():
    sql_db = "sqlite:///budgybot.db"
    printing_press = create_engine(sql_db)
    SQLModel.metadata.create_all(bind=printing_press)

    scribe = RecordsKeeper(printing_press)

    unread_data = find_data(scribe)

    for file in unread_data:
        x = consume_file(file)
        for i, entry in enumerate(x):
            x[i] = entry.map_to_bank_entry()

        scribe.add_multi(sorted(x, key=lambda e: e.transaction_date))


if __name__ == "__main__":
    main()
