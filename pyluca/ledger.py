from pyluca.account_config import BalanceType
from pyluca.aging import get_account_aging
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

    def get_aging(self, account: str):
        return get_account_aging(self.config, self.journal.entries, account, self.journal.entries[-1].date)

