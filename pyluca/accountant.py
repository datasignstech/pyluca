import datetime
import json
from decimal import Decimal, ROUND_UP

from pyluca.journal import Journal, JournalEntry


def round_off_amount(amount: float):
    max_precision = 1e4
    if amount - (int((amount * max_precision)) / max_precision) > 0:
        return float(Decimal(amount).quantize(Decimal('.' + str(int(max_precision))[::-1]), rounding=ROUND_UP))
    return amount


class Accountant:
    def __init__(self, journal: Journal, config: dict, key: str):
        self.journal = journal
        self.config = config
        self.key = key

    def enter_journal(
            self,
            dr_account: str,
            cr_account: str,
            amount: float,
            date: datetime.datetime,
            narration: str
    ):
        amount = round_off_amount(amount)
        if amount == 0:
            return
        self.journal.entries.append(
            JournalEntry(len(self.journal.entries), dr_account, amount, 0, date, narration, self.key))
        self.journal.entries.append(
            JournalEntry(len(self.journal.entries), cr_account, 0, amount, date, narration, self.key))

    def record(self, rule: str, amount: float, date: datetime.datetime, note: str = '', meta: dict = None):
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

    def adjust(self, dr_acct: str, cr_acct: str, amount: float, date: datetime.datetime):
        self.enter_journal(dr_acct, cr_acct, amount, date, 'Reconcile adjust')
