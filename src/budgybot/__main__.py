
import logging
from pathlib import Path

from sqlmodel import create_engine, SQLModel

from budgybot.csv_data import consume_file
from budgybot.records_keeper import RecordsKeeper

log = logging.getLogger(__name__)

cwd = Path(__file__).parent

def main():
    sql_db = "sqlite:///budgybot.db"
    printing_press = create_engine(sql_db)
    SQLModel.metadata.create_all(bind=printing_press)

    scribe = RecordsKeeper(printing_press)



if __name__ == "__main__":
    data_paths = find_data()
    entry_list = list()
    for data_path in data_paths:
        entry_list.append(consume_file(data_path))
    entry_list = sorted(entry_list, key=lambda e: e.date)
    print(entry_list)
