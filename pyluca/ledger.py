from typing import List, Optional
from datetime import datetime
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

    def get_account_dr(self, account: str, as_of: Optional[datetime] = None):
        if as_of is not None:
            return sum([j.dr_amount for j in self.journal.entries if j.account == account and j.date <= as_of])
        return sum([j.dr_amount for j in self.journal.entries if j.account == account])

    def get_account_cr(self, account: str, as_of: Optional[datetime] = None):
        if as_of is not None:
            return sum([j.cr_amount for j in self.journal.entries if j.account == account and j.date <= as_of])
        return sum([j.cr_amount for j in self.journal.entries if j.account == account])

    def get_account_balance(self, account: str, as_of: Optional[datetime] = None):
        assert self.config['accounts'][account]['type'] in self.config['account_types']
        if as_of is not None:
            if self.config['account_types'][self.config['accounts'][account]['type']]['balance_type'] == BalanceType.DEBIT.value:
                return sum([je.dr_amount - je.cr_amount for je in self.journal.entries if je.account == account and je.date <= as_of])
            return sum([je.cr_amount - je.dr_amount for je in self.journal.entries if je.account == account and je.date <= as_of])

        if self.config['account_types'][self.config['accounts'][account]['type']]['balance_type'] == BalanceType.DEBIT.value:
            return sum([je.dr_amount - je.cr_amount for je in self.journal.entries if je.account == account])
        return sum([je.cr_amount - je.dr_amount for je in self.journal.entries if je.account == account])

    def get_balances(self, as_of: Optional[datetime] = None) -> dict:
        accounts_balance = defaultdict(float)
        for je in self.journal.entries:
            if self.config['account_types'][self.config['accounts'][je.account]['type']]['balance_type'] == BalanceType.DEBIT.value:
                if as_of is not None:
                    if je.date <= as_of:
                        accounts_balance[je.account] += (je.dr_amount - je.cr_amount)
                else:
                    accounts_balance[je.account] += (je.dr_amount - je.cr_amount)
            else:
                if as_of is not None:
                    if je.date <= as_of:
                        accounts_balance[je.account] += (je.cr_amount - je.dr_amount)
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
