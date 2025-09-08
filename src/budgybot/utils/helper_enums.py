from enum import StrEnum, auto


class RecordEntry(StrEnum):
    UNDEFINED = auto()
    PAYCHECK = auto()
    DEBIT_EXPENSE = auto()
    CREDIT_EXPENSE = auto()
    CREDIT_PAYMENT = auto()
    RECURRING_MONTHLY = auto()
    RECURRING_YEARLY = auto()


class ChaseDebitEntryType(StrEnum):
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


class ChaseCreditEntryType(StrEnum):
    UNDEFINED = auto()
    ADJUSTMENT = auto()
    FEE = auto()
    PAYMENT = auto()
    RETURN = auto()
    SALE = auto()


class ChaseCreditCategory(StrEnum):
    UNDEFINED = auto()
    AUTOMOTIVE = auto()
    BILLS_UTILITIES = auto()
    ENTERTAINMENT = auto()
    FEES_ADJUSTMENTS = auto()
    FOOD_DRINK = auto()
    GAS = auto()
    GIFTS_DONATIONS = auto()
    GROCERIES = auto()
    HEALTH_WELLNESS = auto()
    HOME = auto()
    PERSONAL = auto()
    PROFESSIONAL_SERVICES = auto()
    SHOPPING = auto()
    TRAVEL = auto()


class DiscoverCreditCategory(StrEnum):
    UNDEFINED = auto()
    SERVICES = auto()
    PAYMENTS = auto()
    RESTAURANTS = auto()
