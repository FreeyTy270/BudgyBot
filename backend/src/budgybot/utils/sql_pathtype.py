from pathlib import Path
from sqlalchemy.types import TypeDecorator, String

"""Credit for this class goes to Claudio Pilotti in this comment: 
https://github.com/fastapi/sqlmodel/issues/397#issuecomment-2426071356"""
class PathType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if isinstance(value, Path):
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return Path(value)
        return value