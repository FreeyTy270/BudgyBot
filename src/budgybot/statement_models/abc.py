from abc import ABC, abstractmethod

from budgybot.records_models import BankEntry


class AbstractEntry(ABC):

    @abstractmethod
    def map_to_bank_entry(self) -> BankEntry:
        pass
