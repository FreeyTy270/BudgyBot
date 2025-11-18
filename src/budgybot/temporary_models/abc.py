from abc import abstractmethod
from typing import Protocol, runtime_checkable

from budgybot.persistent_models.transactions import Transaction


@runtime_checkable
class StatementEntry(Protocol):
    """A protocol for statement entries that can be mapped to a DB Transaction"""

    @abstractmethod
    def map_to_bank_entry(self) -> Transaction: ...
