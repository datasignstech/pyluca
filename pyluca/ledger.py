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

    def get_balance_sheet(self):
        ledger = [_entry.__dict__ for _entry in self.journal.entries]
        for acct_name in self.config['accounts'].keys():
            account_type = self.config['accounts'][acct_name]['type']
            positive_col, negative_col = 'cr_amount', 'dr_amount'
            if self.config['account_types'][account_type]['balance_type'] == BalanceType.DEBIT.value:
                positive_col, negative_col = 'dr_amount', 'cr_amount'
            balance = 0
            for row in ledger:
                if row['account'] == acct_name:
                    balance += row[positive_col]
                    balance -= row[negative_col]
                row[acct_name] = balance
        return ledger
