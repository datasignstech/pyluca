from datetime import datetime
from unittest import TestCase
from collections import defaultdict
from csv import DictReader
from io import StringIO
from pyluca.journal import Journal, JournalEntry
from pyluca.ledger_accountant import LedgerAccountant
from pyluca.tests.test_aging import account_config


class TestLedgerAccountant(TestCase):
    def test_base(self):
        accountant = LedgerAccountant(Journal(), account_config, 'person1')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 20000, datetime(2022, 4, 30), 'April salary')
        self.assertEqual(len(accountant.journal.entries), 2)
        self.assertEqual(accountant.get_account_balance('SAVINGS_BANK'), 20000)
        self.assertEqual(accountant.get_account_balance('SALARY'), 20000)

        accountant.enter_journal('MUTUAL_FUNDS', 'SAVINGS_BANK', 10000, datetime(2022, 5, 1), 'ELSS')
        self.assertEqual(accountant.get_account_balance('SAVINGS_BANK'), 10000)
        self.assertEqual(accountant.get_account_balance('MUTUAL_FUNDS'), 10000)

        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2022, 5, 2), 'Lend to Pramod')
        self.assertEqual(accountant.get_account_balance('LOANS'), 5000)
        self.assertEqual(accountant.get_account_balance('SAVINGS_BANK'), 5000)

        accountant.enter_journal('CAR_EMI', 'SAVINGS_BANK', 3000, datetime(2022, 5, 2), 'EMI 3/48')
        self.assertEqual(accountant.get_account_balance('SAVINGS_BANK'), 2000)

        bal, acct_type_bal = {}, defaultdict(int)
        for acct_name, acct in account_config['accounts'].items():
            bal[acct_name] = accountant.get_account_balance(acct_name)
            acct_type_bal[acct['type']] += bal[acct_name]
        self.assertEqual(acct_type_bal['ASSET'], acct_type_bal['INCOME'] - acct_type_bal['EXPENSE'])

    def test_enter_journal(self):
        accountant = LedgerAccountant(Journal(), account_config, 'person2')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 30000, datetime(2023, 1, 31), 'Jan salary')
        self.assertEqual(accountant.journal.max_date, datetime(2023, 1, 31))
        self.assertRaises(
            AssertionError,
            lambda: accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2023, 1, 1), 'Loans')
        )

    def test_ledger_aging(self):
        dt = datetime.now()
        journal = Journal([
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1'),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1'),
            JournalEntry(3, 'SAVINGS_BANK', 0, 3000, dt, '', '1'),
            JournalEntry(4, 'SAVINGS_BANK', 2000, 0, dt, '', '1'),
        ])
        aging = LedgerAccountant(journal, account_config, '1').get_aging('SAVINGS_BANK')
        self.assertEqual(len(aging.ages), 3)

    def test_balance_sheet(self):
        accountant = LedgerAccountant(Journal(), account_config, '1')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 20000, datetime(2022, 4, 30), 'April salary')
        accountant.enter_journal('MUTUAL_FUNDS', 'SAVINGS_BANK', 10000, datetime(2022, 5, 1), 'ELSS')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2022, 5, 2), 'Lend to Pramod')
        accountant.enter_journal('CAR_EMI', 'SAVINGS_BANK', 3000, datetime(2022, 5, 2), 'EMI 3/48')
        last_row = accountant.get_balance_sheet()[-1]
        self.assertEqual(last_row['SALARY'], 20000)
        self.assertEqual(last_row['SAVINGS_BANK'], 2000)
        self.assertEqual(last_row['MUTUAL_FUNDS'], 10000)
        self.assertEqual(last_row['LOANS'], 5000)
        self.assertEqual(last_row['CAR_EMI'], 3000)

    def test_balance_sheet_csv(self):
        accountant = LedgerAccountant(Journal(), account_config, '1')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 20000, datetime(2022, 4, 30), 'April salary')
        accountant.enter_journal('MUTUAL_FUNDS', 'SAVINGS_BANK', 10000, datetime(2022, 5, 1), 'ELSS')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2022, 5, 2), 'Lend to Pramod')
        accountant.enter_journal('CAR_EMI', 'SAVINGS_BANK', 3000, datetime(2022, 5, 2), 'EMI 3/48')
        balance_sheet = list(DictReader(StringIO(accountant.get_balance_sheet_csv())))
        self.assertEqual(len(balance_sheet), len(accountant.get_balance_sheet()))

    def test_get_account_type_balance(self):
        accountant = LedgerAccountant(Journal(), account_config, '2')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 20000, datetime(2022, 4, 30), 'April salary')
        accountant.enter_journal('MUTUAL_FUNDS', 'SAVINGS_BANK', 10000, datetime(2022, 5, 1), 'ELSS')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2022, 5, 2), 'Lend to Pramod')
        accountant.enter_journal('CAR_EMI', 'SAVINGS_BANK', 3000, datetime(2022, 5, 2), 'EMI 3/48')
        self.assertEqual(17000, accountant.get_account_type_balance('ASSET'))
        self.assertEqual(20000, accountant.get_account_type_balance('INCOME'))
        self.assertEqual(3000, accountant.get_account_type_balance('EXPENSE'))
        self.assertEqual(15000, accountant.get_account_type_balance('ASSET', ['SAVINGS_BANK']))
        self.assertEqual(10000, accountant.get_account_type_balance('ASSET', ['SAVINGS_BANK', 'LOANS']))

    def test_get_accounts_balance(self):
        accountant = LedgerAccountant(Journal(), account_config, '3')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 20000, datetime(2022, 4, 30), 'April salary')
        accountant.enter_journal('MUTUAL_FUNDS', 'SAVINGS_BANK', 10000, datetime(2022, 5, 1), 'ELSS')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2022, 5, 2), 'Lend to Pramod')
        accountant.enter_journal('CAR_EMI', 'SAVINGS_BANK', 3000, datetime(2022, 5, 2), 'EMI 3/48')
        accounts_balance = accountant.get_balances()
        self.assertEqual(accounts_balance['SAVINGS_BANK'], 2000)
        self.assertEqual(accounts_balance['SALARY'], 20000)
        self.assertEqual(accounts_balance['MUTUAL_FUNDS'], 10000)
        self.assertEqual(accounts_balance['LOANS'], 5000)
        self.assertEqual(accounts_balance['CAR_EMI'], 3000)
