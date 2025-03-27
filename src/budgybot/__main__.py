import csv
import json
import logging
from pathlib import Path

from budgybot.statement_models import ChaseCheckingEntry

# from bank_entry import BankEntry, EntryType

log = logging.getLogger(__name__)

cwd = Path(__file__).parent


def consume_file(file: Path) -> list:
    """Reads data in from a csv file located at the Path specified by ``file``. Also
    updates the data held in the consumed file db.

    :param file: Path to the csv file.
    :return: A list of BankEntry objects.
    """
    csv_consumed = []

    with open(file, "r") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            if None in row.keys():
                row.pop(None)
            new_entry = ChaseCheckingEntry(**row)
            csv_consumed.append(new_entry)

    with open(read_file_db, "w+") as f:
        read_files = json.load(f)
        read_files["those_consumed"].append(file.stem)
        json.dump(read_files, f, indent=4)

    return csv_consumed


if __name__ == "__main__":
    data_paths = find_data()
    entry_list = list()
    for data_path in data_paths:
        entry_list.append(consume_file(data_path))
    entry_list = sorted(entry_list, key=lambda e: e.date)
    print(entry_list)
