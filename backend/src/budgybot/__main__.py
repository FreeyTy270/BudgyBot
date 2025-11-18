import logging
import sys

import uvicorn
from sqlmodel import create_engine, SQLModel, select

from budgybot.configurator import SysConf, get_config
from budgybot.csv_records import find_records, loop_and_consume
from budgybot.records import fetch

from budgybot import persistent_models as pms

log = logging.getLogger("buggybot")


def main(conf: SysConf) -> bool:
    sql_db = f"sqlite:///{str(conf.ledger_dir / conf.ledger_name)}.db"
    printing_press = create_engine(sql_db)
    SQLModel.metadata.create_all(bind=printing_press)
    read_files = fetch(printing_press, select(pms.ConsumedStatement.file_name))
    unread_data = find_records(conf.archive_dir, read_files)
    loop_and_consume(printing_press, unread_data)
    return True

if __name__ == "__main__":
    sys_conf = get_config()
    if main(sys_conf):
        uvicorn.run("budgybot.api:app", host="0.0.0.0", port=8000, reload=True)
        sys.exit(0)
    else:
        sys.exit(1)
