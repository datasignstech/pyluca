from typing import List
from collections import defaultdict
import pandas as pd
from pyluca.account_config import BalanceType
from pyluca.aging import get_account_aging
from pyluca.balances import add_account_balance
from pyluca.journal import Journal


class Ledger:
    def __init__(self, journal: Journal, config: dict):
        self.journal = journal
        self.config = config

    def get_account_dr(self, account: str):
        return sum([j.dr_amount for j in self.journal.entries if j.account == account])

    def get_account_cr(self, account: str):
        return sum([j.cr_amount for j in self.journal.entries if j.account == account])

    def get_account_balance(self, account: str):
        assert self.config['accounts'][account]['type'] in self.config['account_types']
        if self.config['account_types'][self.config['accounts'][account]['type']]['balance_type'] == BalanceType.DEBIT.value:
            return self.get_account_dr(account) - self.get_account_cr(account)
        return self.get_account_cr(account) - self.get_account_dr(account)

    def get_balances(self) -> dict:
        accounts_balance = defaultdict(float)
        for je in self.journal.entries:
            if self.config['account_types'][self.config['accounts'][je.account]['type']]['balance_type'] == BalanceType.DEBIT.value:
                accounts_balance[je.account] += (je.dr_amount - je.cr_amount)
            else:
                accounts_balance[je.account] += (je.cr_amount - je.dr_amount)
        return accounts_balance

    def get_df(self) -> pd.DataFrame:
        ledger_df = pd.DataFrame([j.__dict__ for j in self.journal.entries])
        if not ledger_df.empty:
            ledger_df['account_name'] = ledger_df['account'].apply(lambda x: self.config['accounts'][x].get('name', x))
        return ledger_df

    def get_aging(self, account: str):
        return get_account_aging(self.config, self.journal.entries, account, self.journal.entries[-1].date)

    def add_account_balance(self, account: str, df: pd.DataFrame):
        return add_account_balance(self.config, df, account)

    def get_balance_sheet(self):
        df = self.get_df()
        for acct_name in self.config['accounts'].keys():
            df = self.add_account_balance(acct_name, df)
        return df

    def get_account_type_balance(self, account_type: str, exclude_accounts: List[str] = None):
        balance = 0
        exclude_accounts = [] if exclude_accounts is None else exclude_accounts
        for account_name, account in self.config['accounts'].items():
            if account['type'] == account_type and account_name not in exclude_accounts:
                balance += self.get_account_balance(account_name)
        return balance



