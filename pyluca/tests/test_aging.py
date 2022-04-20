from datetime import datetime
from unittest import TestCase

from pyluca.account_config import AccountingConfig
from pyluca.aging import get_account_aging
from pyluca.journal import JournalEntry

account_config = AccountingConfig(dict={
    'account_types': {
        'ASSET': {
            'balance_type': 'DEBIT'
        },
        'INCOME': {
            'balance_type': 'CREDIT'
        },
        'LIABILITY': {
            'balance_type': 'CREDIT'
        },
        'EXPENSE': {
            'balance_type': 'DEBIT'
        }
    },
    'accounts': {
        'SALARY': {'type': 'INCOME'},
        'SAVINGS_BANK': {'type': 'ASSET'},
        'MUTUAL_FUNDS': {'type': 'ASSET'},
        'LOANS': {'type': 'ASSET'},
        'CAR_EMI': {'type': 'EXPENSE'}
    },
    'rules': {}
})


class TestAging(TestCase):
    def test_aging(self):
        dt = datetime.now()
        ages = get_account_aging(account_config, [
            JournalEntry(1, 'SALARY', 1000, 0, dt, '', '1'),
            JournalEntry(2, 'SALARY', 1000, 0, dt, '', '1'),
            JournalEntry(3, 'SALARY', 1000, 0, dt, '', '1'),
            JournalEntry(4, 'SALARY', 0, 4000, dt, '', '1'),
        ], 'SALARY', dt)
        for age in ages:
            self.assertEqual(age.counter.is_paid(), True)

        ages = get_account_aging(account_config, [
            JournalEntry(4, 'SALARY', 0, 4000, dt, '', '1'),
            JournalEntry(1, 'SALARY', 1000, 0, dt, '', '1'),
            JournalEntry(2, 'SALARY', 1000, 0, dt, '', '1'),
            JournalEntry(3, 'SALARY', 1000, 0, dt, '', '1'),
        ], 'SALARY', dt)
        for age in ages:
            self.assertEqual(age.counter.is_paid(), True)

        ages = get_account_aging(account_config, [
            JournalEntry(4, 'SALARY', 0, 3000, dt, '', '1'),
            JournalEntry(1, 'SALARY', 1000, 0, dt, '', '1'),
            JournalEntry(2, 'SALARY', 1000, 0, dt, '', '1'),
            JournalEntry(3, 'SALARY', 2000, 0, dt, '', '1'),
        ], 'SALARY', dt)
        self.assertEqual(len(ages), 3)
        self.assertEqual(ages[0].counter.is_paid(), True)
        self.assertEqual(ages[1].counter.is_paid(), True)
        self.assertEqual(ages[2].counter.is_paid(), False)
        self.assertEqual(ages[2].counter.get_balance(), 1000)

        ages = get_account_aging(account_config, [
            JournalEntry(1, 'SALARY', 1000, 0, dt, '', '1'),
            JournalEntry(2, 'SALARY', 1000, 0, dt, '', '1'),
            JournalEntry(3, 'SALARY', 0, 3000, dt, '', '1'),
            JournalEntry(4, 'SALARY', 2000, 0, dt, '', '1'),
        ], 'SALARY', dt)
        self.assertEqual(len(ages), 3)
        self.assertEqual(ages[0].counter.is_paid(), True)
        self.assertEqual(ages[1].counter.is_paid(), True)
        self.assertEqual(ages[2].counter.is_paid(), False)
        self.assertEqual(ages[2].counter.get_balance(), 1000)
