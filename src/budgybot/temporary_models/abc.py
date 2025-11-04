from abc import abstractmethod
from typing import Protocol

from budgybot.persistent_models.transactions import Transaction


class StatementEntry(Protocol):
    """An abstract base class for statement entries becoming a database object"""

    @abstractmethod
    def map_to_bank_entry(self) -> Transaction:
        pass
