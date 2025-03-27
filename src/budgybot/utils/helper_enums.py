
from enum import Enum, auto

class RecordEntry(Enum):



class ChaseEntryType(Enum):
    ACCT_XFER = auto()
    ACH_CREDIT = auto()
    ACH_DEBIT = auto()
    ATM = auto()
    CHECK_DEPOSIT = auto()
    DEBIT_CARD = auto()
    DEPOSIT = auto()
    FEE_TRANSACTION = auto()
    LOAN_PMT = auto()
    MISC_DEBIT = auto()
    MISC_CREDIT = auto()

