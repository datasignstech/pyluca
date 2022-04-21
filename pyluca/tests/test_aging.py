import json
from datetime import datetime
from unittest import TestCase

from pyluca.account_config import AccountingConfig
from pyluca.accountant import Accountant
from pyluca.aging import get_account_aging
from pyluca.journal import JournalEntry, Journal

account_config = AccountingConfig(**{
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
        'CAR_EMI': {'type': 'EXPENSE'},
        'FREELANCING_INCOME': {'type': 'INCOME'},
        'LOANS_PAYBACK': {'type': 'INCOME'}
    },
    'rules': {}
})


class TestAging(TestCase):
    def test_aging(self):
        dt = datetime.now()
        ages = get_account_aging(account_config, [
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1'),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1'),
            JournalEntry(3, 'SAVINGS_BANK', 1000, 0, dt, '', '1'),
            JournalEntry(4, 'SAVINGS_BANK', 0, 4000, dt, '', '1'),
        ], 'SAVINGS_BANK', dt)
        for age in ages:
            self.assertEqual(age.counter.is_paid(), True)

        ages = get_account_aging(account_config, [
            JournalEntry(4, 'SAVINGS_BANK', 0, 4000, dt, '', '1'),
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1'),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1'),
            JournalEntry(3, 'SAVINGS_BANK', 1000, 0, dt, '', '1'),
        ], 'SAVINGS_BANK', dt)
        for age in ages:
            self.assertEqual(age.counter.is_paid(), True)

        ages = get_account_aging(account_config, [
            JournalEntry(4, 'SAVINGS_BANK', 0, 3000, dt, '', '1'),
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1'),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1'),
            JournalEntry(3, 'SAVINGS_BANK', 2000, 0, dt, '', '1'),
        ], 'SAVINGS_BANK', dt)
        self.assertEqual(len(ages), 3)
        self.assertEqual(ages[0].counter.is_paid(), True)
        self.assertEqual(ages[1].counter.is_paid(), True)
        self.assertEqual(ages[2].counter.is_paid(), False)
        self.assertEqual(ages[2].counter.get_balance(), 1000)

        ages = get_account_aging(account_config, [
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1'),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1'),
            JournalEntry(3, 'SAVINGS_BANK', 0, 3000, dt, '', '1'),
            JournalEntry(4, 'SAVINGS_BANK', 2000, 0, dt, '', '1'),
        ], 'SAVINGS_BANK', dt)
        self.assertEqual(len(ages), 3)
        self.assertEqual(ages[0].counter.is_paid(), True)
        self.assertEqual(ages[1].counter.is_paid(), True)
        self.assertEqual(ages[2].counter.is_paid(), False)
        self.assertEqual(ages[2].counter.get_balance(), 1000)

    def test_meta(self):
        accountant = Accountant(Journal(), account_config, 'person1')
        accountant.enter_journal('SAVINGS_BANK', 'FREELANCING_INCOME', 20000, datetime(2022, 4, 30), 'XYZ client')
        accountant.enter_journal(
            'LOANS', 'SAVINGS_BANK', 1000, datetime(2022, 5, 1),
            f'Lend to Pramod ##{json.dumps({"due_date": "2022-5-5"})}##'
        )
        accountant.enter_journal('LOANS_PAYBACK', 'LOANS', 300, datetime(2022, 5, 10), 'Payback 1')
        accountant.enter_journal('LOANS_PAYBACK', 'LOANS', 200, datetime(2022, 5, 15), 'Payback 2')
        accountant.enter_journal('LOANS_PAYBACK', 'LOANS', 500, datetime(2022, 5, 20), 'Payback 3')
        ages = get_account_aging(account_config, accountant.journal.entries, 'LOANS', datetime(2022, 5, 25))
        self.assertEqual(len(ages), 1)
        self.assertEqual(ages[0].counter.is_paid(), True)
        self.assertEqual(len(ages[0].counter.payments), 3)
        due_meta = ages[0].meta['due_date'].split('-')
        due_date = datetime(int(due_meta[0]), int(due_meta[1]), int(due_meta[2]))
        self.assertEqual((ages[0].counter.get_paid_date() - due_date).days, 15)
