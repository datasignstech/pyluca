from datetime import datetime
from unittest import TestCase

from pyluca.account_config import AccountingConfig
from pyluca.accountant import Accountant
from pyluca.action import apply
from pyluca.event import Event
from pyluca.journal import Journal
from pyluca.ledger import Ledger

personal_fin_config = AccountingConfig(**{
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
        'LOANS_PAYBACK': {'type': 'ASSET'},
        'RISKY_LOANS': {'type': 'ASSET'}
    },
    'rules': {},
    'actions_config': {
        'on_event': {
            'SalaryEvent': {
                'actions': [
                    {
                        'dr_account': 'SAVINGS_BANK',
                        'cr_account': 'SALARY',
                        'amount': 'amount',
                        'narration': 'Salary'
                    }
                ]
            },
            'InvestMFEvent': {
                'actions': [
                    {
                        'dr_account': 'MUTUAL_FUNDS',
                        'cr_account': 'SAVINGS_BANK',
                        'amount': 'amount',
                        'narration': 'Invest in MF'
                    }
                ]
            },
            'LendEvent': {
                'actions': [
                    {
                        'iff': {'operator': '!', 'a': 'risky'},
                        'dr_account': 'LOANS',
                        'cr_account': 'SAVINGS_BANK',
                        'amount': 'amount',
                        'narration': 'Lend',
                        'meta': {
                            'due_date': 'due_date'
                        }
                    },
                    {
                        'iff': 'risky',
                        'dr_account': 'RISKY_LOANS',
                        'cr_account': 'SAVINGS_BANK',
                        'amount': 'amount',
                        'narration': 'Risky lend',
                        'meta': {
                            'due_date': 'due_date'
                        }
                    }
                ]
            },
            'ClearLoansEvent': {
                'actions': [
                    {
                        'dr_account': 'LOANS_PAYBACK',
                        'cr_account': 'LOANS',
                        'amount': 'balance.LOANS',
                        'narration': 'Clear off loans'
                    }
                ]
            },
            'LiquidLoanRepayments': {
                'actions': [
                    {
                        'dr_account': 'SAVINGS_BANK',
                        'cr_account': 'LOANS_PAYBACK',
                        'amount': 'balance.LOANS_PAYBACK',
                        'narration': 'Liquidate loans payback'
                    }
                ]
            }
        }
    }
})


class AmountEvent(Event):
    def __init__(
            self,
            event_id: str,
            amount: float,
            date: datetime,
            created_date: datetime,
            created_by: str = None
    ):
        self.amount = amount
        super(AmountEvent, self).__init__(event_id, date, created_date, created_by)


class SalaryEvent(AmountEvent):
    pass


class InvestMFEvent(AmountEvent):
    pass


class LendEvent(AmountEvent):
    def __init__(
            self,
            event_id: str,
            amount: float,
            due_date: str,
            date: datetime,
            created_date: datetime,
            created_by: str = None,
            risky: bool = False
    ):
        self.due_date = due_date
        self.risky = risky
        super(LendEvent, self).__init__(event_id, amount, date, created_date, created_by)


class ClearLoansEvent(Event):
    pass


class LiquidLoanRepayments(Event):
    pass


class TestAction(TestCase):
    def test_config(self):
        AccountingConfig(**{
            'account_types': {},
            'accounts': {},
            'rules': {}
        })
        config = AccountingConfig(**{
            'account_types': {},
            'accounts': {},
            'rules': {},
            'actions_config': {
                'on_event': {
                    'Salary': {
                        'actions': [
                            {
                                'dr_account': 'X',
                                'cr_account': 'Y',
                                'amount': 'amount',
                                'narration': 'test'
                            }
                        ]
                    }
                }
            }
        })
        action = config.actions_config.on_event['Salary'].actions[0]
        self.assertEqual(action.type, None)
        self.assertEqual(action.dr_account, 'X')
        self.assertEqual(action.cr_account, 'Y')
        self.assertEqual(action.amount, 'amount')
        self.assertEqual(action.narration, 'test')

    def test_base(self):
        accountant = Accountant(Journal(), personal_fin_config, '1')
        event = SalaryEvent('1', 20000, datetime(2022, 4, 21), datetime(2022, 4, 21))
        apply(event, accountant)
        ledger = Ledger(accountant.journal, accountant.config)
        self.assertEqual(ledger.get_account_balance('SALARY'), 20000)
        self.assertEqual(ledger.get_account_balance('SAVINGS_BANK'), 20000)

        event = InvestMFEvent('2', 10000, datetime(2022, 4, 21), datetime(2022, 4, 21))
        apply(event, accountant)
        ledger = Ledger(accountant.journal, accountant.config)
        self.assertEqual(ledger.get_account_balance('SALARY'), 20000)
        self.assertEqual(ledger.get_account_balance('SAVINGS_BANK'), 10000)
        self.assertEqual(ledger.get_account_balance('MUTUAL_FUNDS'), 10000)

        event = LendEvent('3', 5000, '2022-6-21', datetime(2022, 4, 21), datetime(2022, 4, 21))
        apply(event, accountant)
        ledger = Ledger(accountant.journal, accountant.config)
        self.assertEqual(ledger.get_account_balance('SAVINGS_BANK'), 5000)
        self.assertEqual(ledger.get_account_balance('LOANS'), 5000)
        ages = ledger.get_aging('LOANS')
        self.assertEqual(ages[0].meta, {'due_date': '2022-6-21'})

        event = ClearLoansEvent('4', datetime(2022, 4, 25), datetime(2022, 4, 25))
        apply(event, accountant)
        ledger = Ledger(accountant.journal, accountant.config)
        self.assertEqual(ledger.get_account_balance('LOANS'), 0)
        ages = ledger.get_aging('LOANS')
        self.assertEqual(ages[0].counter.get_paid_date(), datetime(2022, 4, 25))

        event = LendEvent('5', 5000, '2022-6-21', datetime(2022, 4, 26), datetime(2022, 4, 26), risky=True)
        apply(event, accountant)
        ledger = Ledger(accountant.journal, accountant.config)
        self.assertEqual(ledger.get_account_balance('LOANS'), 0)
        self.assertEqual(ledger.get_account_balance('RISKY_LOANS'), 5000)
        self.assertEqual(ledger.get_account_balance('SAVINGS_BANK'), 0)

        apply(LiquidLoanRepayments('7', datetime(2022, 4, 29), datetime(2022, 4, 29)), accountant)
        ledger = Ledger(accountant.journal, accountant.config)
        self.assertEqual(ledger.get_account_balance('LOANS'), 0)
        self.assertEqual(ledger.get_account_balance('LOANS_PAYBACK'), 0)
        self.assertEqual(ledger.get_account_balance('SAVINGS_BANK'), 5000)