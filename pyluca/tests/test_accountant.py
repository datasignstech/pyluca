from collections import defaultdict
from datetime import datetime
from unittest import TestCase

from pyluca.accountant import Accountant
from pyluca.journal import Journal, InvalidEntryException
from pyluca.ledger import Ledger
from pyluca.tests.test_aging import account_config


class TestAccountant(TestCase):
    def test_base(self):
        accountant = Accountant(Journal(), account_config, 'person1')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 20000, datetime(2022, 4, 30), 'April salary')
        self.assertEqual(len(accountant.journal.entries), 2)
        self.assertEqual(accountant.ledger.get_account_balance('SAVINGS_BANK'), 20000)
        self.assertEqual(accountant.ledger.get_account_balance('SALARY'), 20000)
        self.assertEqual(len(accountant.ledger.get_df()), 2)

        accountant.enter_journal('MUTUAL_FUNDS', 'SAVINGS_BANK', 10000, datetime(2022, 5, 1), 'ELSS')
        self.assertEqual(accountant.ledger.get_account_balance('SAVINGS_BANK'), 10000)
        self.assertEqual(accountant.ledger.get_account_balance('MUTUAL_FUNDS'), 10000)

        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2022, 5, 2), 'Lend to Pramod')
        self.assertEqual(accountant.ledger.get_account_balance('LOANS'), 5000)
        self.assertEqual(accountant.ledger.get_account_balance('SAVINGS_BANK'), 5000)

        accountant.enter_journal('CAR_EMI', 'SAVINGS_BANK', 3000, datetime(2022, 5, 2), 'EMI 3/48')
        self.assertEqual(accountant.ledger.get_account_balance('SAVINGS_BANK'), 2000)

        bal, ledger, acct_type_bal = {}, Ledger(accountant.journal, accountant.config), defaultdict(int)
        for acct_name, acct in account_config['accounts'].items():
            bal[acct_name] = ledger.get_account_balance(acct_name)
            acct_type_bal[acct['type']] += bal[acct_name]
        self.assertEqual(acct_type_bal['ASSET'], acct_type_bal['INCOME'] - acct_type_bal['EXPENSE'])

    def test_enter_journal(self):
        accountant = Accountant(Journal(), account_config, 'person2')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 30000, datetime(2023, 1, 31), 'Jan salary')
        self.assertEqual(accountant.journal.max_date, datetime(2023, 1, 31))

        self.assertRaises(
            InvalidEntryException,
            lambda: accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2023, 1, 1), 'Loans')
        )
