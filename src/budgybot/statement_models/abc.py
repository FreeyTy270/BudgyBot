from abc import ABC, abstractmethod

from budgybot.records_models import BankEntry


class AbstractStatementEntry(ABC):
    """An abstract base class for statement entries becoming a database object"""

    @abstractmethod
    def map_to_bank_entry(self) -> BankEntry:
        pass
