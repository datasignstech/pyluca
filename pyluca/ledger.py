import pandas as pd

from account_config import AccountingConfig
from journal import Journal


class Ledger:
    def __init__(self, journal: Journal, config: AccountingConfig):
        self.journal = journal
        self.config = config

    def get_account_dr(self, account: str):
        return sum([j.dr_amount for j in self.journal.entries if j.account == account])

    def get_account_cr(self, account: str):
        return sum([j.cr_amount for j in self.journal.entries if j.account == account])

    def get_account_balance(self, account: str):
        assert self.config.ACCOUNTS[account].type in self.config.ACCOUNT_TYPES
        if self.config.ACCOUNTS[account].type in self.config.DEBIT_BALANCE_ACCOUNT_TYPES:
            return self.get_account_dr(account) - self.get_account_cr(account)
        return self.get_account_cr(account) - self.get_account_dr(account)

    def get_df(self) -> pd.DataFrame:
        return pd.DataFrame([j.__dict__ for j in self.journal.entries])
