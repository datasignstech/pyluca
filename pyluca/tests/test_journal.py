from datetime import datetime
from unittest import TestCase
from pyluca.journal import Journal, JournalEntry, InvalidEntryException


class TestJournal(TestCase):
    def test_add_journal_entry(self):
        journal = Journal()
        self.assertEqual(journal.max_date, None)

        journal.add_entry(JournalEntry(1, 'SAVINGS_BANK', 30000, 0, datetime(2023, 1, 31), 'Jan Salary', 'person2', None))
        journal.add_entry(JournalEntry(2, 'SALARY', 0, 30000, datetime(2023, 1, 31), 'Jan Salary', 'person2', None))
        self.assertEqual(len(journal.entries), 2)
        self.assertEqual(journal.max_date, datetime(2023, 1, 31))

        journal = Journal(entries=[
                JournalEntry(1, 'SAVINGS_BANK', 30000, 0, datetime(2023, 1, 31), 'Jan Salary', 'person2', None),
                JournalEntry(2, 'SALARY', 0, 30000, datetime(2023, 1, 31), 'Jan Salary', 'person2', None),
                JournalEntry(3, 'LOANS', 5000, 0, datetime(2023, 2, 1), 'Lend to person2', 'person2', None),
                JournalEntry(4, 'SAVINGS_BANK', 0, 5000, datetime(2023, 2, 1), 'Lend to person2', 'person2', None)
            ])
        self.assertEqual(journal.max_date, datetime(2023, 2, 1))

        journal.add_entry(JournalEntry(5, 'LOANS_PAYBACK', 2500, 0, datetime(2023, 2, 2), 'Loans Payback', 'person2', None))
        journal.add_entry(JournalEntry(6, 'LOANS', 0, 2500, datetime(2023, 2, 2), 'Loans Payback', 'person2', None))
        self.assertEqual(journal.max_date, datetime(2023, 2, 2))

        self.assertRaises(InvalidEntryException, lambda: journal.add_entry(
            JournalEntry(7, 'SAVINGS_BANK', 2000, 0, datetime(2023, 2, 1), 'Invest something', 'person2', None)
        ))


