from abc import ABC, abstractmethod


class AbstractEntry(ABC):

    @abstractmethod
    def map_to_bank_entry(self):
        pass
