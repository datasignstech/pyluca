from enum import Enum
from typing import Dict

from pydictable.core import DictAble
from pydictable.field import StrField, DictValueField, EnumField


class BalanceType(Enum):
    CREDIT = 'CREDIT'
    DEBIT = 'DEBIT'


class Account(DictAble):
    type: str = StrField(required=True)


class Rule(DictAble):
    narration: str = StrField(required=True)
    dr_account: str = StrField(required=True)
    cr_account: str = StrField(required=True)


class AccountType(DictAble):
    balance_type: BalanceType = EnumField(BalanceType, required=True)


class AccountingConfig(DictAble):
    account_types: Dict[str, AccountType] = DictValueField(AccountType, required=True)
    accounts: Dict[str, Account] = DictValueField(Account, required=True)
    rules: Dict[str, Rule] = DictValueField(Rule, required=True)

    def get_account_names(self):
        return self.accounts.keys()
