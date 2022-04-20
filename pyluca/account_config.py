from typing import List, Dict

from pydictable.core import DictAble
from pydictable.field import ListField, StrField, DictValueField


class AccountConfig(DictAble):
    type: str = StrField(required=True)


class RuleConfig(DictAble):
    narration: str = StrField(required=True)
    dr_account: str = StrField(required=True)
    cr_account: str = StrField(required=True)


class AccountingConfig(DictAble):
    account_types: List[str] = ListField(StrField(), required=True)
    debit_balance_account_types: List[str] = ListField(StrField(), required=True)
    credit_balance_account_types: List[str] = ListField(StrField(), required=True)
    accounts: Dict[str, AccountConfig] = DictValueField(AccountConfig)
    rules: Dict[str, RuleConfig] = DictValueField(RuleConfig)
