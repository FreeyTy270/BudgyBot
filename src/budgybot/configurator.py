from pathlib import Path
from tomllib import load
from pydantic import BaseModel, field_validator, ValidationError

from budgybot.__main__ import log

cwd = Path(__file__).parent


class SysConf(BaseModel):
    archive_dir: Path
    ledger_name: str
    ledger_dir: Path

    @field_validator('ledger_dir', 'archive_dir')
    @classmethod
    def validate_conf_paths(cls, conf_path: str) -> Path:
        str_as_path = Path(conf_path)
        if str_as_path.is_dir and not str_as_path.exists():
            log.info(f'Path {str_as_path} does not exist; Making Directory')
            str_as_path.mkdir(parents=True)
        elif str_as_path.is_file() and not str_as_path.parent.exists():
            log.info(f'Path {str_as_path.parent} does not exist; Making Directory')
            str_as_path.parent.mkdir(parents=True)


def get_config():
    conf_path = cwd / 'budgy_conf.toml'

    with open(conf_path, 'rb') as f:
        raw_conf = load(f)

    try:
        sys_conf = SysConf(**raw_conf['SYSTEM'])
    except ValidationError as e:
        log.error(e)
        log.info(f'BudgyBot configuration is invalid: Check System Config @'
                 f' {conf_path}')
        raise e

    return sys_conf
