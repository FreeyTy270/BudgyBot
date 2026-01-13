from budgybot.persistent_models.banks import (
    Bank,
    BankPublic,
    BankCreate,
    BankAccount,
    BankAccountPublic,
    BankAccountPublicWithTransactions,
    BankAccountUpdate,
    BankAccountCreate,
)
from budgybot.persistent_models.transactions import (
    Transaction,
    TransactionPublic,
    TransactionPublicWithAccount,
    ConsumedStatement,
)
from budgybot.persistent_models.pay import Salary, Pay
from budgybot.persistent_models.users import UserProfile


TransactionPublicWithAccount.model_rebuild(
    _types_namespace={"BankAccountPublic": BankAccountPublic}
)
