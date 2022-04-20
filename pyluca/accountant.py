import datetime
import json

from account_config import AccountingConfig
from journal import Journal, JournalEntry


class Accountant:
    def __init__(self, journal: Journal, config: AccountingConfig, key: str):
        self.journal = journal
        self.config = config
        self.key = key

    def enter_journal(
            self,
            dr_account: str,
            cr_account: str,
            amount: float,
            date: datetime.datetime,
            narration: str,
            index: str
    ):
        if amount == 0:
            return
        self.journal.entries.append(JournalEntry(len(self.journal.entries), dr_account, amount, 0, date, narration, index))
        self.journal.entries.append(JournalEntry(len(self.journal.entries), cr_account, 0, amount, date, narration, index))

    def record(self, rule: str, amount: float, date: datetime.datetime, note: str = '', meta: dict = None):
        rule = self.config.RULES[rule]
        narration = f'{rule.narration} {note}'
        if meta:
            narration = f'{narration} ##{json.dumps(meta)}##'
        if amount > 0:
            self.enter_journal(
                rule.dr_account,
                rule.cr_account,
                amount,
                date,
                narration,
                self.key
            )

    def adjust(self, dr_acct: str, cr_acct: str, amount: float, date: datetime.datetime):
        self.enter_journal(dr_acct, cr_acct, amount, date, 'Reconcile adjust', self.key)
