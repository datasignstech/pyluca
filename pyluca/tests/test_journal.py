from datetime import datetime
from unittest import TestCase

from pyluca.journal import Journal, JournalEntry

from pyluca.accountant import Accountant
from pyluca.tests.test_aging import account_config


class TestJournal(TestCase):
    def test_add_journal_entry(self):
        accountant = Accountant(Journal(), account_config, 'person2')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 30000, datetime(2023, 1, 31), 'Jan salary')
        self.assertEqual(accountant.journal.max_date, datetime(2023, 1, 31))

        self.assertRaises(
            AssertionError,
            lambda: accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2023, 1, 1), 'Loans')
        )

        accountant = Accountant(
            Journal(entries=[
                JournalEntry(1, 'SAVINGS_BANK', 30000, 0, datetime(2023, 1, 31), 'Jan Salary', 'person2'),
                JournalEntry(2, 'SALARY', 0, 30000, datetime(2023, 1, 31), 'Jan Salary', 'person2'),
                JournalEntry(3, 'LOANS', 5000, 0, datetime(2023, 2, 1), 'Lend to person2', 'person2'),
                JournalEntry(4, 'SAVINGS_BANK', 0, 5000, datetime(2023, 2, 1), 'Lend to person2', 'person2')
            ]), account_config, 'person2')
        self.assertEqual(accountant.journal.max_date, datetime(2023, 2, 1))

