import logging

from sqlmodel import create_engine, SQLModel

from budgybot.configurator import SysConf, get_config
from budgybot.csv_records import find_records, loop_and_consume

log = logging.getLogger()


def main(conf: SysConf) -> None:
    sql_db = f"sqlite:///{str(conf.ledger_dir / conf.ledger_name)}.db"
    printing_press = create_engine(sql_db)
    SQLModel.metadata.create_all(bind=printing_press)

    unread_data = find_records(printing_press)
    loop_and_consume(printing_press, unread_data)



if __name__ == "__main__":
    sys_conf = get_config()
    main(sys_conf)
