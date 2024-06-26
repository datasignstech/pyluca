import datetime
import json
from typing import Optional
from pyluca.journal import Journal, JournalEntry
from pyluca.ledger import Ledger


class Accountant:
    def __init__(self, journal: Journal, config: dict, key: str):
        self.journal = journal
        self.config = config
        self.key = key
        self.ledger = Ledger(journal, config, key)

    def enter_journal(
            self,
            dr_account: str,
            cr_account: str,
            amount: float,
            date: datetime.datetime,
            narration: str,
            event_id: Optional[str] = None
    ):
        if amount == 0:
            return
        self.journal.add_entry(
            JournalEntry(len(self.journal.entries), dr_account, amount, 0, date, narration, self.key, event_id))
        self.journal.add_entry(
            JournalEntry(len(self.journal.entries), cr_account, 0, amount, date, narration, self.key, event_id))
        self.ledger.add_entry(dr_account, cr_account, amount, date, narration, event_id)

    def record(
            self,
            rule: str,
            amount: float,
            date: datetime.datetime,
            note: str = '',
            meta: dict = None,
            event_id: Optional[str] = None
    ):
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
                narration,
                event_id
            )

    def adjust(self, dr_acct: str, cr_acct: str, amount: float, date: datetime.datetime):
        self.enter_journal(dr_acct, cr_acct, amount, date, 'Reconcile adjust')
