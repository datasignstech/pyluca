from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel


class BalanceType(Enum):
    CREDIT = 'CREDIT'
    DEBIT = 'DEBIT'


class Account(BaseModel):
    type: str


class Rule(BaseModel):
    narration: str
    dr_account: str
    cr_account: str


class Operator(BaseModel):
    type: str
    a: str
    b: Optional[str]


class AccountType(BaseModel):
    balance_type: BalanceType


class Action(BaseModel):
    type: Optional[str]
    dr_account: Optional[str]
    cr_account: Optional[str]
    amount: Optional[Union[str, Operator]]
    narration: Optional[str]
    meta: Optional[Dict[str, str]]
    iff: Optional[Union[Operator, str]]


class EventAction(BaseModel):
    narration: Optional[str]
    actions: List[Action]


class ActionsConfig(BaseModel):
    on_event: Dict[str, EventAction]


class AccountingConfig(BaseModel):
    account_types: Dict[str, AccountType]
    accounts: Dict[str, Account]
    rules: Dict[str, Rule]
    actions_config: Optional[ActionsConfig]

    def get_account_names(self):
        return self.accounts.keys()
