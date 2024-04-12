from typing import List, Optional, NamedTuple, Dict
from datetime import datetime
import pandas as pd
from pyluca.account_config import BalanceType
from pyluca.balances import add_account_balance
from pyluca.journal import Journal


class InvalidLedgerEntry(Exception):
    pass


class LedgerEntry(NamedTuple):
    date: datetime
    dr_amount: float
    cr_amount: float
    narration: str
    balance: float
    event_id: Optional[str]
    sl_no: Optional[int]


class AccountLedger:
    def __init__(self, account_name: str, balance_type: BalanceType):
        self.account_name = account_name
        self.balance_type = balance_type
        self.__entries: List[LedgerEntry] = []

    def add_entry(
            self,
            date: datetime,
            dr_amount: float,
            cr_amount: float,
            narration: str,
            event_id: Optional[str],
            sl_no: Optional[int],
    ):
        if len(self.__entries) and date < self.__entries[-1].date:
            raise InvalidLedgerEntry("Backdated entry can't be added")
        balance = self.__entries[-1].balance if len(self.__entries) else 0
        balance += dr_amount - cr_amount if self.balance_type == BalanceType.DEBIT else cr_amount - dr_amount
        self.__entries.append(
            LedgerEntry(
                sl_no=sl_no,
                date=date,
                dr_amount=dr_amount,
                cr_amount=cr_amount,
                narration=narration,
                balance=balance,
                event_id=event_id
            )
        )

    def get_balance(self, as_of: Optional[datetime] = None) -> float:
        if as_of is None:
            return self.__entries[-1].balance if len(self.__entries) else 0

        balance = 0
        start, end = 0, len(self.__entries) - 1
        while start <= end:
            mid = (start + end) // 2
            if self.__entries[mid].date <= as_of:
                balance = self.__entries[mid].balance
                start = mid + 1
            else:
                end = mid - 1
        return balance

    def get_entries(self) -> List[LedgerEntry]:
        return self.__entries


class Ledger:
    def __init__(self, journal: Journal, config: dict, key: str = ""):
        self.config = config
        self.key = key
        self.ledgers: Dict[str, AccountLedger] = {
            account: AccountLedger(
                account_name=account_config.get('name', account),
                balance_type=BalanceType[config['account_types'][account_config['type']]['balance_type']]
            )
            for account, account_config in config['accounts'].items()
        }
        self.__sl_no: int = 0
        for je in journal.entries:
            self.ledgers[je.account].add_entry(
                date=je.date,
                dr_amount=je.dr_amount,
                cr_amount=je.cr_amount,
                narration=je.narration,
                event_id=je.event_id,
                sl_no=self.__sl_no
            )
            self.__sl_no += 1

    def add_entry(
            self,
            dr_account: str,
            cr_account: str,
            amount: float,
            date: datetime,
            narration: str,
            event_id: Optional[str] = None
    ):
        self.ledgers[dr_account].add_entry(
            date=date,
            dr_amount=amount,
            cr_amount=0,
            narration=narration,
            event_id=event_id,
            sl_no=self.__sl_no
        )
        self.__sl_no += 1
        self.ledgers[cr_account].add_entry(
            date=date,
            dr_amount=0,
            cr_amount=amount,
            narration=narration,
            event_id=event_id,
            sl_no=self.__sl_no
        )
        self.__sl_no += 1

    def get_account_dr(self, account: str, as_of: Optional[datetime] = None) -> float:
        assert self.config['accounts'][account]['type'] in self.config['account_types'], f'Invalid account {account}'
        if as_of is not None:
            return sum([entry.dr_amount for entry in self.ledgers[account].get_entries() if entry.date <= as_of])
        return sum([entry.dr_amount for entry in self.ledgers[account].get_entries()])

    def get_account_cr(self, account: str, as_of: Optional[datetime] = None) -> float:
        assert self.config['accounts'][account]['type'] in self.config['account_types'], f'Invalid account {account}'
        if as_of is not None:
            return sum([entry.cr_amount for entry in self.ledgers[account].get_entries() if entry.date <= as_of])
        return sum([entry.cr_amount for entry in self.ledgers[account].get_entries()])

    def get_account_balance(self, account: str, as_of: Optional[datetime] = None) -> float:
        assert self.config['accounts'][account]['type'] in self.config['account_types'], f'Invalid account {account}'
        return self.ledgers[account].get_balance(as_of)

    def get_balances(self, as_of: Optional[datetime] = None) -> Dict[str, float]:
        return {account: ledger.get_balance(as_of) for account, ledger in self.ledgers.items()}

    def get_ledger(self) -> List[dict]:
        return sorted(
            [
                {**entry._asdict(), 'account': account, 'key': self.key}
                for account, ledger in self.ledgers.items()
                for entry in ledger.get_entries()
            ],
            key=lambda x: x['sl_no']
        )

    def get_df(self) -> pd.DataFrame:
        ledger_df = pd.DataFrame(self.get_ledger())
        ledger_df.drop(columns=['balance'], inplace=True)
        if not ledger_df.empty:
            ledger_df['account_name'] = ledger_df['account'].apply(lambda x: self.config['accounts'][x].get('name', x))
        return ledger_df

    def add_account_balance(self, account: str, df: pd.DataFrame):
        return add_account_balance(self.config, df, account)

    def get_balance_sheet(self):
        df = self.get_df()
        for acct_name in self.config['accounts'].keys():
            df = self.add_account_balance(acct_name, df)
        return df

    def get_account_type_balance(self, account_type: str, exclude_accounts: List[str] = None):
        balance = 0
        exclude_accounts = [] if exclude_accounts is None else exclude_accounts
        for account_name, account in self.config['accounts'].items():
            if account['type'] == account_type and account_name not in exclude_accounts:
                balance += self.get_account_balance(account_name)
        return balance
