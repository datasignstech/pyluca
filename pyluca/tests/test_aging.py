import json
from datetime import datetime
from unittest import TestCase
from pyluca.accountant import Accountant
from pyluca.aging import get_account_aging, get_accounts_aging
from pyluca.journal import JournalEntry, Journal
from pyluca.ledger import Ledger

account_config = {
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
        'SALARY': {'type': 'INCOME', 'name': 'SALARY_AMOUNT'},
        'SAVINGS_BANK': {'type': 'ASSET', 'name': 'SAVINGS_ACCOUNT'},
        'MUTUAL_FUNDS': {'type': 'ASSET'},
        'LOANS': {'type': 'ASSET'},
        'CAR_EMI': {'type': 'EXPENSE'},
        'FREELANCING_INCOME': {'type': 'INCOME'},
        'LOANS_PAYBACK': {'type': 'INCOME'}
    },
    'rules': {}
}


class TestAging(TestCase):
    def test_aging(self):
        dt = datetime.now()
        aging = get_account_aging(account_config, [
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(3, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(4, 'SAVINGS_BANK', 0, 4000, dt, '', '1', None),
        ], 'SAVINGS_BANK', dt)
        for age in aging.ages:
            self.assertEqual(age.counter.is_paid(), True)

        aging = get_account_aging(account_config, [
            JournalEntry(4, 'SAVINGS_BANK', 0, 4000, dt, '', '1', None),
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(3, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
        ], 'SAVINGS_BANK', dt)
        for age in aging.ages:
            self.assertEqual(age.counter.is_paid(), True)

        aging = get_account_aging(account_config, [
            JournalEntry(4, 'SAVINGS_BANK', 0, 3000, dt, '', '1', None),
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(3, 'SAVINGS_BANK', 2000, 0, dt, '', '1', None),
        ], 'SAVINGS_BANK', dt)
        self.assertEqual(len(aging.ages), 3)
        self.assertEqual(aging.ages[0].counter.is_paid(), True)
        self.assertEqual(aging.ages[1].counter.is_paid(), True)
        self.assertEqual(aging.ages[2].counter.is_paid(), False)
        self.assertEqual(aging.ages[2].counter.get_balance(), 1000)

        aging = get_account_aging(account_config, [
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(3, 'SAVINGS_BANK', 0, 3000, dt, '', '1', None),
            JournalEntry(4, 'SAVINGS_BANK', 2000, 0, dt, '', '1', None),
        ], 'SAVINGS_BANK', dt)
        self.assertEqual(len(aging.ages), 3)
        self.assertEqual(aging.ages[0].counter.is_paid(), True)
        self.assertEqual(aging.ages[1].counter.is_paid(), True)
        self.assertEqual(aging.ages[2].counter.is_paid(), False)
        self.assertEqual(aging.ages[2].counter.get_balance(), 1000)

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
        aging = get_account_aging(account_config, accountant.journal.entries, 'LOANS', datetime(2022, 5, 25))
        self.assertEqual(len(aging.ages), 1)
        self.assertEqual(aging.ages[0].counter.is_paid(), True)
        self.assertEqual(len(aging.ages[0].counter.payments), 3)
        due_meta = aging.ages[0].meta['due_date'].split('-')
        due_date = datetime(int(due_meta[0]), int(due_meta[1]), int(due_meta[2]))
        self.assertEqual((aging.ages[0].counter.payments[-1].date - due_date).days, 15)

    def test_high_precision(self):
        accountant = Accountant(Journal(), account_config, 'person1')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 200, datetime(2022, 8, 9), 'Salary')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 100.128839293829282838283823, datetime(2022, 8, 10), 'XYZ client')
        accountant.enter_journal('LOANS_PAYBACK', 'LOANS', 100.12883, datetime(2022, 8, 10), 'XYZ client')
        aging = get_account_aging(account_config, accountant.journal.entries, 'LOANS', datetime(2022, 8, 11))
        age = aging.ages[0]
        self.assertTrue(age.counter.is_paid())
        self.assertAlmostEqual(age.counter.get_balance(), 0, 4)

        accountant = Accountant(Journal(), account_config, 'person1')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 200, datetime(2022, 8, 9), 'Salary')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 100.128839293829282838283823, datetime(2022, 8, 10),
                                 'XYZ client')
        accountant.enter_journal('LOANS_PAYBACK', 'LOANS', 100.1288, datetime(2022, 8, 10), 'XYZ client')
        aging = get_account_aging(account_config, accountant.journal.entries, 'LOANS', datetime(2022, 8, 11))
        age = aging.ages[0]
        self.assertFalse(age.counter.is_paid())

        accountant = Accountant(Journal(), account_config, 'person1')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 200, datetime(2022, 8, 9), 'Salary')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 100.00000387278, datetime(2022, 8, 10),
                                 'To a')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 200.00000387278, datetime(2022, 8, 10),
                                 'To b')
        accountant.enter_journal('LOANS_PAYBACK', 'LOANS', 100, datetime(2022, 8, 10), 'From a')
        accountant.enter_journal('LOANS_PAYBACK', 'LOANS', 199.999994222222222, datetime(2022, 8, 10), 'From b')
        aging = get_account_aging(account_config, accountant.journal.entries, 'LOANS', datetime(2022, 8, 11))
        age1, age2 = aging.ages[0], aging.ages[1]
        self.assertTrue(age1.counter.is_paid())
        self.assertTrue(age2.counter.is_paid())
        self.assertNotEqual(age1.counter.get_balance(), 0)
        self.assertNotEqual(age2.counter.get_balance(), 0)
        ledger = Ledger(accountant.journal, accountant.config)
        self.assertAlmostEqual(ledger.get_account_balance('LOANS'), 0, 4)

    def test_aging_state(self):
        accountant = Accountant(Journal(), account_config, 'person1')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 200, datetime(2022, 8, 9), 'Salary')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 100, datetime(2022, 8, 10),
                                 'To a')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 200, datetime(2022, 8, 10),
                                 'To b')
        aging = get_account_aging(account_config, accountant.journal.entries, 'LOANS', datetime(2022, 8, 10))
        self.assertEqual(aging.last_sl_no, 4)
        self.assertEqual(len(aging.ages), 2)
        accountant.enter_journal('LOANS_PAYBACK', 'LOANS', 100, datetime(2022, 8, 10), 'From a')
        accountant.enter_journal('LOANS_PAYBACK', 'LOANS', 199, datetime(2022, 8, 10), 'From b')
        aging = get_account_aging(
            account_config, accountant.journal.entries, 'LOANS', datetime(2022, 8, 10), previous_aging=aging
        )
        self.assertEqual(Ledger(accountant.journal, accountant.config).get_account_balance('LOANS'), 1)
        self.assertEqual(aging.ages[0].counter.get_balance(), 0)
        self.assertEqual(aging.ages[1].counter.get_balance(), 1)
        self.assertEqual(aging.last_sl_no, 9)
        self.assertEqual(len(aging.ages), 2)

        try:
            get_account_aging(
                account_config, accountant.journal.entries, 'SAVINGS_BANK', datetime(2022, 8, 10), previous_aging=aging
            )
            raise AssertionError('Should not have passed because wrong previous state provided')
        except ValueError as e:
            self.assertEqual(str(e), 'Invalid previous aging! account not matching')

    def test_get_accounts_aging(self):
        dt = datetime.now()
        aging = get_accounts_aging(account_config, [
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(3, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(4, 'SAVINGS_BANK', 0, 4000, dt, '', '1', None),
        ], ['SAVINGS_BANK'], dt)
        for age in aging['SAVINGS_BANK'].ages:
            self.assertEqual(age.counter.is_paid(), True)

        aging = get_accounts_aging(account_config, [
            JournalEntry(4, 'SAVINGS_BANK', 0, 4000, dt, '', '1', None),
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(3, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
        ], ['SAVINGS_BANK'], dt)
        for age in aging['SAVINGS_BANK'].ages:
            self.assertEqual(age.counter.is_paid(), True)

        aging = get_accounts_aging(account_config, [
            JournalEntry(4, 'SAVINGS_BANK', 0, 3000, dt, '', '1', None),
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(3, 'SAVINGS_BANK', 2000, 0, dt, '', '1', None),
        ], ['SAVINGS_BANK'], dt)
        ages = aging['SAVINGS_BANK'].ages
        self.assertEqual(len(ages), 3)
        self.assertEqual(ages[0].counter.is_paid(), True)
        self.assertEqual(ages[1].counter.is_paid(), True)
        self.assertEqual(ages[2].counter.is_paid(), False)
        self.assertEqual(ages[2].counter.get_balance(), 1000)

        aging = get_accounts_aging(account_config, [
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(3, 'SAVINGS_BANK', 0, 3000, dt, '', '1', None),
            JournalEntry(4, 'SAVINGS_BANK', 2000, 0, dt, '', '1', None),
        ], ['SAVINGS_BANK'], dt)
        ages = aging['SAVINGS_BANK'].ages
        self.assertEqual(len(ages), 3)
        self.assertEqual(ages[0].counter.is_paid(), True)
        self.assertEqual(ages[1].counter.is_paid(), True)
        self.assertEqual(ages[2].counter.is_paid(), False)
        self.assertEqual(ages[2].counter.get_balance(), 1000)

    def test_aging_state_with_get_accounts_aging(self):
        accountant = Accountant(Journal(), account_config, 'person1')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 200, datetime(2022, 8, 9), 'Salary')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 100, datetime(2022, 8, 10), 'To a')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 200, datetime(2022, 8, 10), 'To b')
        aging = get_accounts_aging(
            account_config, accountant.journal.entries, ['SAVINGS_BANK', 'LOANS'], datetime(2022, 8, 10)
        )

        saving_bank_aging = aging['SAVINGS_BANK']
        self.assertEqual(len(saving_bank_aging.ages), 1)
        self.assertEqual(saving_bank_aging.ages[0].counter.is_paid(), True)
        self.assertEqual(saving_bank_aging.ages[0].counter.get_balance(), 0)
        self.assertEqual(saving_bank_aging.excess_amount, 100)
        self.assertEqual(saving_bank_aging.last_sl_no, 5)
        self.assertEqual(saving_bank_aging.last_unpaid_age_idx, 1)

        loans_aging = aging['LOANS']
        self.assertEqual(len(loans_aging.ages), 2)
        self.assertEqual(loans_aging.ages[0].counter.is_paid(), False)
        self.assertEqual(loans_aging.ages[0].counter.get_balance(), 100)
        self.assertEqual(loans_aging.ages[1].counter.is_paid(), False)
        self.assertEqual(loans_aging.ages[1].counter.get_balance(), 200)
        self.assertEqual(loans_aging.excess_amount, 0)
        self.assertEqual(loans_aging.last_sl_no, 4)
        self.assertEqual(loans_aging.last_unpaid_age_idx, 0)

        accountant.enter_journal('LOANS_PAYBACK', 'LOANS', 100, datetime(2022, 8, 11), 'From a')
        accountant.enter_journal('LOANS_PAYBACK', 'LOANS', 199, datetime(2022, 8, 12), 'From b')
        aging = get_accounts_aging(
            account_config, accountant.journal.entries, ['LOANS'],
            datetime(2022, 8, 12), previous_aging=aging
        )
        loans_aging = aging['LOANS']
        self.assertEqual(len(loans_aging.ages), 2)
        self.assertEqual(loans_aging.ages[0].counter.is_paid(), True)
        self.assertEqual(loans_aging.ages[0].counter.get_balance(), 0)
        self.assertEqual(loans_aging.ages[1].counter.is_paid(), False)
        self.assertEqual(loans_aging.ages[1].counter.get_balance(), 1)
        self.assertEqual(loans_aging.excess_amount, 0)
        self.assertEqual(loans_aging.last_sl_no, 9)
        self.assertEqual(loans_aging.last_unpaid_age_idx, 1)

        with self.assertRaises(ValueError) as e:
            get_accounts_aging(
                account_config, accountant.journal.entries, ['LOANS_PAYBACK'],
                datetime(2022, 8, 12), previous_aging=aging
            )
        self.assertEqual(e.exception.__str__(), 'Invalid previous aging! accounts not matching')

    def test_with_meta_ac_payments(self):
        accountant = Accountant(Journal(), account_config, 'person1')
        accountant.enter_journal('SAVINGS_BANK', 'LOANS', 200, datetime(2022, 8, 9), 'Salary', 'event1')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 50, datetime(2022, 8, 10), 'To a', 'event2')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 150, datetime(2022, 8, 10), 'To b', 'event3')
        aging = get_account_aging(
            account_config, accountant.journal.entries, 'SAVINGS_BANK', datetime(2022, 8, 10)
        )
        age = aging.ages[0]
        self.assertEqual(age.counter.is_paid(), True)
        self.assertEqual(len(age.counter.payments), 2)
        self.assertEqual(age.counter.payments[0].amount, 50)
        self.assertEqual(age.counter.payments[0].meta['entry']['event_id'], 'event2')
        self.assertEqual(age.counter.payments[1].meta['entry']['event_id'], 'event3')

        agings = get_accounts_aging(
            account_config, accountant.journal.entries, ['SAVINGS_BANK', 'LOANS'], datetime(2022, 8, 10)
        )
        age = agings['SAVINGS_BANK'].ages[0]
        self.assertEqual(age.counter.payments[0].meta['entry']['event_id'], 'event2')
        self.assertEqual(age.counter.payments[1].meta['entry']['event_id'], 'event3')

