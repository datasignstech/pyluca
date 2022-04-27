from datetime import datetime
from unittest import TestCase

from pyluca.accountant import Accountant
from pyluca.journal import Journal, JournalEntry
from pyluca.ledger import Ledger
from pyluca.tests.test_aging import account_config


class TestLedger(TestCase):
    def test_ledger_aging(self):
        dt = datetime.now()
        journal = Journal([
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1'),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1'),
            JournalEntry(3, 'SAVINGS_BANK', 0, 3000, dt, '', '1'),
            JournalEntry(4, 'SAVINGS_BANK', 2000, 0, dt, '', '1'),
        ])
        ages = Ledger(journal, account_config).get_aging('SAVINGS_BANK')
        self.assertEqual(len(ages), 3)
