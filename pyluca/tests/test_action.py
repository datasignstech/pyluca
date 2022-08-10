from datetime import datetime
from unittest import TestCase
from pyluca.accountant import Accountant
from pyluca.action import apply
from pyluca.event import Event
from pyluca.journal import Journal
from pyluca.ledger import Ledger

personal_fin_config = {
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
        'RISKY_LOANS': {'type': 'ASSET'},
        'MUTUAL_FUNDS_PNL': {'type': 'INCOME'},
        'CHARITY': {'type': 'EXPENSE'},
        'FIXED_DEPOSIT': {'type': 'ASSET'}
    },
    'rules': {},
    'actions_config': {
        'common_actions': {
            'charity': {
                'actions': [
                    {
                        'dr_account': 'CHARITY',
                        'cr_account': 'SAVINGS_BANK',
                        'amount': {'type': '*', 'a': 'amount', 'b': 0.01},
                        'narration': 'Give charity to {context.to} on {context.date}'
                    }
                ]
            },
            'fd': {
                'actions': [
                    {
                        'dr_account': 'FIXED_DEPOSIT',
                        'cr_account': 'SAVINGS_BANK',
                        'amount': 'context.another_amount',
                        'narration': 'Put in fixed deposit for {context.sub_narration}'
                    }
                ]
            }
        },
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
                        'iff': {'type': '!', 'a': 'risky'},
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
            'LiquidLoanRepaymentsEvent': {
                'actions': [
                    {
                        'dr_account': 'SAVINGS_BANK',
                        'cr_account': 'LOANS_PAYBACK',
                        'amount': 'balance.LOANS_PAYBACK',
                        'narration': 'Liquidate loans payback'
                    }
                ]
            },
            'MFProfitEvent': {
                'actions': [
                    {
                        'dr_account': 'MUTUAL_FUNDS',
                        'cr_account': 'MUTUAL_FUNDS_PNL',
                        'amount': {
                            'type': '*',
                            'a': 'context.multiplier',
                            'b': 'balance.MUTUAL_FUNDS'
                        },
                        'narration': 'Mutual fund P&L'
                    }
                ]
            },
            'FreelancingSalaryEvent': {
                'actions': [
                    {
                        'dr_account': 'SAVINGS_BANK',
                        'cr_account': 'SALARY',
                        'amount': 'amount',
                        'narration': 'Salary'
                    },
                    {
                        'type': 'action.charity',
                        'context': {
                            'to': 'str.TATA Trusts',
                            'date': 'str.10/05/2022'
                        }
                    },
                    {
                        'type': 'action.fd',
                        'context': {
                            'another_amount': {'type': '*', 'a': 'amount', 'b': 0.09},
                            'sub_narration': 'str.Freelancing salary'
                        }
                    }
                ]
            }
        }
    }
}


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


class LiquidLoanRepaymentsEvent(Event):
    pass


class MFProfitEvent(Event):
    pass


class FreelancingSalaryEvent(AmountEvent):
    pass


class TestAction(TestCase):
    def test_config(self):
        config = {
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
        }
        action = config['actions_config']['on_event']['Salary']['actions'][0]
        self.assertEqual(action.get('type'), None)
        self.assertEqual(action['dr_account'], 'X')
        self.assertEqual(action['cr_account'], 'Y')
        self.assertEqual(action['amount'], 'amount')
        self.assertEqual(action['narration'], 'test')

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
        self.assertEqual(ages[0].counter.payments[-1].date, datetime(2022, 4, 25))

        event = LendEvent('5', 5000, '2022-6-21', datetime(2022, 4, 26), datetime(2022, 4, 26), risky=True)
        apply(event, accountant)
        ledger = Ledger(accountant.journal, accountant.config)
        self.assertEqual(ledger.get_account_balance('LOANS'), 0)
        self.assertEqual(ledger.get_account_balance('RISKY_LOANS'), 5000)
        self.assertEqual(ledger.get_account_balance('SAVINGS_BANK'), 0)

        apply(LiquidLoanRepaymentsEvent('7', datetime(2022, 4, 29), datetime(2022, 4, 29)), accountant)
        ledger = Ledger(accountant.journal, accountant.config)
        self.assertEqual(ledger.get_account_balance('LOANS'), 0)
        self.assertEqual(ledger.get_account_balance('LOANS_PAYBACK'), 0)
        self.assertEqual(ledger.get_account_balance('SAVINGS_BANK'), 5000)

    def test_context(self):
        accountant = Accountant(Journal(), personal_fin_config, '1')
        events = [
            SalaryEvent('1', 20000, datetime(2022, 4, 21), datetime(2022, 4, 21)),
            InvestMFEvent('2', 20000, datetime(2022, 4, 21), datetime(2022, 4, 21)),
            MFProfitEvent('3', datetime(2022, 4, 30), datetime(2022, 4, 30))
        ]
        for e in events:
            apply(e, accountant, {'multiplier': .18})
        ledger = Ledger(accountant.journal, accountant.config)
        self.assertEqual(ledger.get_account_balance('MUTUAL_FUNDS'), 20000 * 1.18)
        self.assertEqual(ledger.get_account_balance('MUTUAL_FUNDS_PNL'), 20000 * .18)

    def test_common_action(self):
        accountant = Accountant(Journal(), personal_fin_config, '1')
        events = [
            FreelancingSalaryEvent('1', 20000, datetime(2022, 4, 21), datetime(2022, 4, 21))
        ]
        for e in events:
            apply(e, accountant)
        ledger = Ledger(accountant.journal, accountant.config)
        self.assertEqual(ledger.get_account_balance('CHARITY'), 200)
        self.assertEqual(ledger.get_account_balance('FIXED_DEPOSIT'), 1800)
        self.assertEqual(ledger.get_account_balance('SAVINGS_BANK'), 20000 - 200 - 1800)

    def test_sub_narration(self):
        accountant = Accountant(Journal(), personal_fin_config, '1')
        events = [
            FreelancingSalaryEvent('1', 20000, datetime(2022, 4, 21), datetime(2022, 4, 21))
        ]
        for e in events:
            apply(e, accountant)
        for je in Ledger(accountant.journal, accountant.config).journal.entries:
            if je.account == 'CHARITY':
                self.assertEqual(je.narration, 'Give charity to TATA Trusts on 10/05/2022')
            if je.account == 'FIXED_DEPOSIT':
                self.assertEqual(je.narration, 'Put in fixed deposit for Freelancing salary')
