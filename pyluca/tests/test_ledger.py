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

    def test_ledger_balance_sheet(self):
        accountant = Accountant(Journal(), account_config, '1')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 20000, datetime(2022, 4, 30), 'April salary')
        accountant.enter_journal('MUTUAL_FUNDS', 'SAVINGS_BANK', 10000, datetime(2022, 5, 1), 'ELSS')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2022, 5, 2), 'Lend to Pramod')
        accountant.enter_journal('CAR_EMI', 'SAVINGS_BANK', 3000, datetime(2022, 5, 2), 'EMI 3/48')
        ledger = Ledger(accountant.journal, account_config)
        last_row = ledger.get_balance_sheet().to_dict(orient='record')[-1]
        self.assertEqual(last_row['SALARY'], 20000)
        self.assertEqual(last_row['SAVINGS_BANK'], 2000)
        self.assertEqual(last_row['MUTUAL_FUNDS'], 10000)
        self.assertEqual(last_row['LOANS'], 5000)
        self.assertEqual(last_row['CAR_EMI'], 3000)
