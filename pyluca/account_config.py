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
    ACCOUNT_TYPES: List[str] = ListField(StrField(), required=True)
    DEBIT_BALANCE_ACCOUNT_TYPES: List[str] = ListField(StrField(), required=True)
    CREDIT_BALANCE_ACCOUNT_TYPES: List[str] = ListField(StrField(), required=True)
    ACCOUNTS: Dict[str, AccountConfig] = DictValueField(AccountConfig)
    RULES: Dict[str, RuleConfig] = DictValueField(RuleConfig)
