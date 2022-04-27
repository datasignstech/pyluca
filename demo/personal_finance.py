from pyluca.accountant import Accountant
from pyluca.action import apply
from pyluca.event import Event
from pyluca.journal import Journal
from pyluca.ledger import Ledger
from datetime import datetime


'''
Basic usage
'''

config = {
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
}

accountant = Accountant(Journal(), config, 'person1')
accountant.enter_journal('SAVINGS_BANK', 'SALARY', 20000, datetime(2022, 4, 30), 'March salary')
accountant.enter_journal('MUTUAL_FUNDS', 'SAVINGS_BANK', 10000, datetime(2022, 5, 1), 'Invest in NIFTY 50 Index')
accountant.enter_journal('CAR_EMI', 'SAVINGS_BANK', 5000, datetime(2022, 5, 5), '5th EMI')
accountant.enter_journal('LOANS', 'SAVINGS_BANK', 3000, datetime(2022, 5, 5), 'Lend to Kalyan')

ledger = Ledger(accountant.journal, accountant.config)
assert ledger.get_account_balance('SAVINGS_BANK') == 2000
assert ledger.get_account_balance('SALARY') == 20000
assert ledger.get_account_balance('LOANS') == 3000
assert ledger.get_account_balance('CAR_EMI') == 5000

accountant.enter_journal('SAVINGS_BANK', 'LOANS', 2000, datetime(2022, 5, 15), 'Partial payback')
ledger = Ledger(accountant.journal, accountant.config)
assert ledger.get_account_balance('LOANS') == 1000
assert ledger.get_account_balance('SAVINGS_BANK') == 4000


'''
Events & Actions
'''


class AmountEvent(Event):
    """
    An abstract Event which contains amount in it
    """
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


class InvestMutualFundEvent(AmountEvent):
    pass


class LendEvent(AmountEvent):
    pass


class CollectionEvent(AmountEvent):
    pass


config_dict = {
    **config,  # Just extending above config
    'actions_config': {
        'on_event': {
            'SalaryEvent': {
                'actions': [
                    {
                        'dr_account': 'SAVINGS_BANK',
                        'cr_account': 'SALARY',
                        'amount': 'amount',
                        'narration': 'Salary credit'
                    }
                ]
            },
            'InvestMutualFundEvent': {
                'actions': [
                    {
                        'dr_account': 'MUTUAL_FUNDS',
                        'cr_account': 'SAVINGS_BANK',
                        'amount': 'amount',
                        'narration': 'Invest in mutual funds'
                    }
                ]
            },
            'LendEvent': {
                'actions': [
                    {
                        'dr_account': 'LOANS',
                        'cr_account': 'SAVINGS_BANK',
                        'amount': 'amount',
                        'narration': 'Lend'
                    }
                ]
            },
            'CollectionEvent': {
                'actions': [
                    {
                        'dr_account': 'SAVINGS_BANK',
                        'cr_account': 'LOANS',
                        'amount': 'amount',
                        'narration': 'Collection for the loan'
                    }
                ]
            }
        }
    }
}

events = [
    SalaryEvent('salary', 20000, datetime(2022, 4, 30), datetime(2022, 4, 30)),
    InvestMutualFundEvent('mf-1', 10000, datetime(2022, 5, 2), datetime(2022, 5, 2)),
    LendEvent('lend-1', 5000, datetime(2022, 5, 4), datetime(2022, 5, 4))
]

accountant = Accountant(Journal(), config_dict, 'person-1')
for event in events:
    apply(event, accountant)

ledger = Ledger(accountant.journal, accountant.config)
assert ledger.get_account_balance('SALARY') == 20000
assert ledger.get_account_balance('MUTUAL_FUNDS') == 10000
assert ledger.get_account_balance('LOANS') == 5000

events = [
    CollectionEvent('coll-1', 3000, datetime(2022, 5, 20), datetime(2022, 5, 20)),
]
for event in events:
    apply(event, accountant)
assert ledger.get_account_balance('LOANS') == 2000


'''
Ledger as of some time in past
'''


def get_ledger_as_of(acctnt: Accountant, as_of: datetime):
    return Ledger(Journal([e for e in acctnt.journal.entries if e.date <= as_of]), acctnt.config)


assert get_ledger_as_of(accountant, datetime(2022, 4, 29)).get_account_balance('SAVINGS_BANK') == 0
assert get_ledger_as_of(accountant, datetime(2022, 4, 30)).get_account_balance('SAVINGS_BANK') == 20000
assert get_ledger_as_of(accountant, datetime(2022, 5, 2)).get_account_balance('SAVINGS_BANK') == 10000
assert get_ledger_as_of(accountant, datetime(2022, 5, 4)).get_account_balance('SAVINGS_BANK') == 5000
assert get_ledger_as_of(accountant, datetime(2022, 5, 20)).get_account_balance('SAVINGS_BANK') == 8000

assert get_ledger_as_of(accountant, datetime(2022, 5, 3, 23, 59, 59, 999)).get_account_balance('LOANS') == 0
assert get_ledger_as_of(accountant, datetime(2022, 5, 4, 0, 0, 0, 1)).get_account_balance('LOANS') == 5000
assert get_ledger_as_of(accountant, datetime(2022, 5, 20)).get_account_balance('LOANS') == 2000
