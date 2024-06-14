import json
from datetime import datetime
from typing import List
from collections import defaultdict
from io import StringIO
from csv import DictWriter
from pyluca.journal import Journal, JournalEntry
from pyluca.account_config import BalanceType
from pyluca.aging import get_account_aging


class LedgerAccountant:
    def __init__(self, journal: Journal, config: dict, key: str):
        self.journal: Journal = journal
        self.config: dict = config
        self.key: str = key
        self.__balances: dict = defaultdict(float)
        self.__balance_sheet: List[dict] = []

    def get_balance_type(self, account: str) -> str:
        return self.config['account_types'][self.config['accounts'][account]['type']]['balance_type']

    def __update_dr_account_balances(self, dr_account: str, amount: float):
        if self.get_balance_type(dr_account) == BalanceType.DEBIT.value:
            self.__balances[dr_account] += amount
        else:
            self.__balances[dr_account] -= amount

    def __update_cr_account_balances(self, cr_account: str, amount: float):
        if self.get_balance_type(cr_account) == BalanceType.CREDIT.value:
            self.__balances[cr_account] += amount
        else:
            self.__balances[cr_account] -= amount

    def __update_balance_sheet(self, je: JournalEntry):
        self.__balance_sheet.append({**je.__dict__, **self.__balances})

    def enter_journal(
            self,
            dr_account: str,
            cr_account: str,
            amount: float,
            date: datetime,
            narration: str
    ):
        if amount == 0:
            return

        debit_entry = JournalEntry(len(self.journal.entries), dr_account, amount, 0, date, narration, self.key)
        self.journal.add_entry(debit_entry)
        self.__update_dr_account_balances(dr_account, amount)
        self.__update_balance_sheet(debit_entry)

        credit_entry = JournalEntry(len(self.journal.entries), cr_account, 0, amount, date, narration, self.key)
        self.journal.add_entry(credit_entry)
        self.__update_cr_account_balances(cr_account, amount)
        self.__update_balance_sheet(credit_entry)

    def record(self, rule: str, amount: float, date: datetime, note: str = '', meta: dict = None):
        rule = self.config['rules'][rule]
        narration = f'{rule["narration"]} {note}'
        if meta:
            narration = f'{narration} ##{json.dumps(meta)}##'
        if amount > 0:
            self.enter_journal(
                rule['dr_account'],
                rule['cr_account'],
                amount,
                date,
                narration
            )

    def adjust(self, dr_acct: str, cr_acct: str, amount: float, date: datetime):
        self.enter_journal(dr_acct, cr_acct, amount, date, 'Reconcile adjust')

    def get_account_balance(self, account: str) -> float:
        return self.__balances[account]

    def get_balances(self) -> dict:
        return self.__balances

    def get_aging(self, account: str):
        return get_account_aging(self.config, self.journal.entries, account, self.journal.entries[-1].date)

    def get_balance_sheet(self) -> List[dict]:
        return self.__balance_sheet

    def get_balance_sheet_csv(self, field_names: List[str] = None) -> str:
        csv_buffer = StringIO()
        if not field_names:
            field_names = ['sl_no', 'account', 'dr_amount', 'cr_amount', 'date', 'narration', 'key'] \
               + list(self.config['accounts'].keys())
        dict_writer = DictWriter(csv_buffer, field_names)
        dict_writer.writeheader()
        dict_writer.writerows(self.get_balance_sheet())
        return csv_buffer.getvalue()

    def get_account_type_balance(self, account_type: str, exclude_accounts: List[str] = None):
        balance = 0
        exclude_accounts = [] if exclude_accounts is None else exclude_accounts
        for account_name, account in self.config['accounts'].items():
            if account['type'] == account_type and account_name not in exclude_accounts:
                balance += self.get_account_balance(account_name)
        return balance
