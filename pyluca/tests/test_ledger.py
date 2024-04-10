from datetime import datetime
from unittest import TestCase
from pyluca.accountant import Accountant
from pyluca.journal import Journal, JournalEntry
from pyluca.ledger import Ledger, AccountLedger, InvalidLedgerEntry
from pyluca.account_config import BalanceType
from pyluca.tests.test_aging import account_config

sample_ledger_entries = [
    {
        'sl_no': 1,
        'date': datetime(2024, 3, 1),
        'dr_amount': 0,
        'cr_amount': 20000,
        'narration': 'salary credited',
        'balance': 20000,
        'event_id': None
    },
    {
        'sl_no': 2,
        'date': datetime(2024, 3, 2),
        'dr_amount': 5000,
        'cr_amount': 0,
        'narration': 'home loan emi',
        'balance': 15000,
        'event_id': None
    },
    {
        'sl_no': 3,
        'date': datetime(2024, 3, 3),
        'dr_amount': 3000,
        'cr_amount': 0,
        'narration': 'bike emi',
        'balance': 12000,
        'event_id': None
    },
    {
        'sl_no': 4,
        'date': datetime(2024, 3, 4),
        'dr_amount': 10000,
        'cr_amount': 0,
        'narration': 'Rent',
        'balance': 2000,
        'event_id': None
    },
    {
        'sl_no': 5,
        'date': datetime(2024, 3, 5),
        'dr_amount': 0,
        'cr_amount': 5000,
        'narration': 'borrowed from friend',
        'balance': 7000,
        'event_id': None
    },
    {
        'sl_no': 6,
        'date': datetime(2024, 3, 6),
        'dr_amount': 4000,
        'cr_amount': 0,
        'narration': 'SIP Investment',
        'balance': 3000,
        'event_id': None
    },
    {
        'sl_no': 7,
        'date': datetime(2024, 3, 6),
        'balance': 2000,
        'cr_amount': 0,
        'dr_amount': 1000,
        'event_id': None,
        'narration': 'shopping'
    }
]


class TestLedger(TestCase):
    def test_ledger_aging(self):
        dt = datetime.now()
        journal = Journal([
            JournalEntry(1, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(2, 'SAVINGS_BANK', 1000, 0, dt, '', '1', None),
            JournalEntry(3, 'SAVINGS_BANK', 0, 3000, dt, '', '1', None),
            JournalEntry(4, 'SAVINGS_BANK', 2000, 0, dt, '', '1', None),
        ])
        aging = Ledger(journal, account_config).get_aging('SAVINGS_BANK')
        self.assertEqual(len(aging.ages), 3)

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

    def test_get_account_type_balance(self):
        accountant = Accountant(Journal(), account_config, '2')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 20000, datetime(2022, 4, 30), 'April salary')
        accountant.enter_journal('MUTUAL_FUNDS', 'SAVINGS_BANK', 10000, datetime(2022, 5, 1), 'ELSS')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2022, 5, 2), 'Lend to Pramod')
        accountant.enter_journal('CAR_EMI', 'SAVINGS_BANK', 3000, datetime(2022, 5, 2), 'EMI 3/48')
        ledger = Ledger(accountant.journal, account_config)
        self.assertEqual(17000, ledger.get_account_type_balance('ASSET'))
        self.assertEqual(20000, ledger.get_account_type_balance('INCOME'))
        self.assertEqual(3000, ledger.get_account_type_balance('EXPENSE'))

        self.assertEqual(15000, ledger.get_account_type_balance('ASSET', ['SAVINGS_BANK']))
        self.assertEqual(10000, ledger.get_account_type_balance('ASSET', ['SAVINGS_BANK', 'LOANS']))

    def test_account_name_ledger_df(self):
        accountant = Accountant(Journal(), account_config, '2')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 20000, datetime(2022, 4, 30), 'April salary')
        accountant.enter_journal('MUTUAL_FUNDS', 'SAVINGS_BANK', 10000, datetime(2022, 5, 1), 'ELSS')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2022, 5, 2), 'Lend to Pramod')
        accountant.enter_journal('CAR_EMI', 'SAVINGS_BANK', 3000, datetime(2022, 5, 2), 'EMI 3/48')
        ledger = Ledger(accountant.journal, account_config)
        ledger_df = ledger.get_df()
        self.assertEqual(
            'SAVINGS_ACCOUNT',
            ledger_df[ledger_df['account'] == 'SAVINGS_BANK'].reset_index()._get_value(0, 'account_name')
        )
        self.assertEqual(
            'SALARY_AMOUNT',
            ledger_df[ledger_df['account'] == 'SALARY'].reset_index()._get_value(0, 'account_name')
        )

    def test_get_accounts_balance(self):
        accountant = Accountant(Journal(), account_config, '3')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 20000, datetime(2022, 4, 30), 'April salary')
        accountant.enter_journal('MUTUAL_FUNDS', 'SAVINGS_BANK', 10000, datetime(2022, 5, 1), 'ELSS')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2022, 5, 2), 'Lend to Pramod')
        accountant.enter_journal('CAR_EMI', 'SAVINGS_BANK', 3000, datetime(2022, 5, 2), 'EMI 3/48')
        ledger = Ledger(accountant.journal, account_config)
        accounts_balance = ledger.get_balances()
        self.assertEqual(accounts_balance['SAVINGS_BANK'], 2000)
        self.assertEqual(accounts_balance['SALARY'], 20000)
        self.assertEqual(accounts_balance['MUTUAL_FUNDS'], 10000)
        self.assertEqual(accounts_balance['LOANS'], 5000)
        self.assertEqual(accounts_balance['CAR_EMI'], 3000)

    def test_get_account_balance_as_of(self):
        accountant = Accountant(Journal(), account_config, '3')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 20000, datetime(2022, 4, 30), 'April salary')
        accountant.enter_journal('MUTUAL_FUNDS', 'SAVINGS_BANK', 10000, datetime(2022, 5, 1), 'ELSS')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2022, 5, 2), 'Lend to Pramod')
        accountant.enter_journal('CAR_EMI', 'SAVINGS_BANK', 3000, datetime(2022, 5, 2), 'EMI 3/48')
        ledger = Ledger(accountant.journal, account_config)
        self.assertEqual(ledger.get_account_balance('SAVINGS_BANK', datetime(2022, 4, 29)), 0)
        self.assertEqual(ledger.get_account_balance('SAVINGS_BANK', datetime(2022, 4, 30)), 20000)
        self.assertEqual(ledger.get_account_balance('SAVINGS_BANK', datetime(2022, 5, 1)), 10000)
        self.assertEqual(ledger.get_account_balance('SAVINGS_BANK', datetime(2022, 5, 2)), 2000)
        self.assertEqual(
            ledger.get_account_balance('SAVINGS_BANK'),
            ledger.get_account_balance('SAVINGS_BANK', datetime(2022, 5, 2))
        )

    def test_get_accounts_balance_as_of(self):
        accountant = Accountant(Journal(), account_config, '3')
        accountant.enter_journal('SAVINGS_BANK', 'SALARY', 20000, datetime(2022, 4, 30), 'April salary')
        accountant.enter_journal('MUTUAL_FUNDS', 'SAVINGS_BANK', 10000, datetime(2022, 5, 1), 'ELSS')
        accountant.enter_journal('LOANS', 'SAVINGS_BANK', 5000, datetime(2022, 5, 2), 'Lend to Pramod')
        accountant.enter_journal('CAR_EMI', 'SAVINGS_BANK', 3000, datetime(2022, 5, 2), 'EMI 3/48')
        ledger = Ledger(accountant.journal, account_config)

        accounts_balance = ledger.get_balances(datetime(2022, 4, 29))
        self.assertEqual(accounts_balance['SAVINGS_BANK'], 0)
        self.assertEqual(accounts_balance['SALARY'], 0)
        self.assertEqual(accounts_balance['MUTUAL_FUNDS'], 0)
        self.assertEqual(accounts_balance['LOANS'], 0)
        self.assertEqual(accounts_balance['CAR_EMI'], 0)

        accounts_balance = ledger.get_balances(datetime(2022, 4, 30))
        self.assertEqual(accounts_balance['SAVINGS_BANK'], 20000)
        self.assertEqual(accounts_balance['SALARY'], 20000)

        accounts_balance = ledger.get_balances(datetime(2022, 5, 1))
        self.assertEqual(accounts_balance['SAVINGS_BANK'], 10000)
        self.assertEqual(accounts_balance['MUTUAL_FUNDS'], 10000)

        accounts_balance = ledger.get_balances(datetime(2022, 5, 2))
        self.assertEqual(accounts_balance['SAVINGS_BANK'], 2000)
        self.assertEqual(accounts_balance['LOANS'], 5000)
        self.assertEqual(accounts_balance['CAR_EMI'], 3000)

        self.assertEqual(ledger.get_balances(), ledger.get_balances(datetime(2022, 5, 2)))

    def test_account_ledger(self):
        ledger = AccountLedger("Savings", BalanceType.CREDIT)
        ledger.add_entry(sl_no=1, date=datetime(2024, 3, 1), dr_amount=0, cr_amount=20000, narration="salary credited",
                         event_id=None)
        self.assertEqual(ledger.get_balance(), 20000)
        self.assertEqual(ledger.get_balance(as_of=datetime(2024, 2, 29)), 0)
        self.assertEqual(ledger.get_balance(as_of=datetime(2024, 3, 1)), 20000)
        self.assertEqual(ledger.get_balance(as_of=datetime(2024, 3, 2)), 20000)
        with self.assertRaises(InvalidLedgerEntry) as e:
            ledger.add_entry(sl_no=2, date=datetime(2024, 2, 29), dr_amount=5000, cr_amount=0, narration="loan emi",
                             event_id=None)
        self.assertEqual(e.exception.__str__(), "Backdated entry can't be added")
        ledger.add_entry(sl_no=2, date=datetime(2024, 3, 2), dr_amount=5000, cr_amount=0, narration="home loan emi",
                         event_id=None)
        ledger.add_entry(sl_no=3, date=datetime(2024, 3, 3), dr_amount=3000, cr_amount=0, narration="bike emi",
                         event_id=None)
        ledger.add_entry(sl_no=4, date=datetime(2024, 3, 4), dr_amount=10000, cr_amount=0, narration="Rent",
                         event_id=None)
        ledger.add_entry(sl_no=5, date=datetime(2024, 3, 5), dr_amount=0, cr_amount=5000, narration="borrowed from friend",
                         event_id=None)
        ledger.add_entry(sl_no=6, date=datetime(2024, 3, 6), dr_amount=4000, cr_amount=0, narration="SIP Investment",
                         event_id=None)
        ledger.add_entry(sl_no=7, date=datetime(2024, 3, 6), dr_amount=1000, cr_amount=0, narration="shopping",
                         event_id=None)
        self.assertEqual(ledger.get_balance(), 2000)
        self.assertEqual(ledger.get_balance(as_of=datetime(2024, 3, 2)), 15000)
        self.assertEqual(ledger.get_balance(as_of=datetime(2024, 3, 3)), 12000)
        self.assertEqual(ledger.get_balance(as_of=datetime(2024, 3, 4)), 2000)
        self.assertEqual(ledger.get_balance(as_of=datetime(2024, 3, 5)), 7000)
        self.assertEqual(ledger.get_balance(as_of=datetime(2024, 3, 6)), 2000)
        self.assertEqual(ledger.get_balance(as_of=datetime(2024, 3, 7)), 2000)
        self.assertEqual([entry._asdict() for entry in ledger.get_entries()], sample_ledger_entries)

        ledger = AccountLedger("Asset", BalanceType.DEBIT)
        ledger.add_entry(sl_no=1, date=datetime(2024, 3, 1), dr_amount=5000, cr_amount=0, narration="lent to friend",
                         event_id=None)
        ledger.add_entry(sl_no=2, date=datetime(2024, 3, 2), dr_amount=0, cr_amount=2000, narration="received 2000",
                         event_id=None)
        ledger.add_entry(sl_no=3, date=datetime(2024, 3, 3), dr_amount=3000, cr_amount=0, narration="Invested in stock",
                         event_id=None)
        self.assertEqual(ledger.get_balance(), 6000)
        self.assertEqual(ledger.get_balance(as_of=datetime(2024, 2, 29)), 0)
        self.assertEqual(ledger.get_balance(as_of=datetime(2024, 3, 1)), 5000)
        self.assertEqual(ledger.get_balance(as_of=datetime(2024, 3, 2)), 3000)
        self.assertEqual(ledger.get_balance(as_of=datetime(2024, 3, 3)), 6000)
        self.assertEqual(ledger.get_balance(as_of=datetime(2024, 3, 4)), 6000)
