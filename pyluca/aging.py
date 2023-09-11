import json
import re
from datetime import datetime
from typing import NamedTuple, List, Optional, Dict, Tuple
from pyluca.account_config import BalanceType
from pyluca.journal import JournalEntry
from pyluca.amount_counter import AmountCounter


class AccountAge(NamedTuple):
    date: datetime
    counter: AmountCounter
    meta: Optional[dict]
    journal_entry: JournalEntry


class AccountAging:
    def __init__(
            self,
            account: str,
            ages: List[AccountAge],
            excess_amount: float,
            last_sl_no: int,
            last_unpaid_age_idx: int = 0
    ):
        self.account = account
        self.ages = ages
        self.excess_amount = excess_amount
        self.last_sl_no = last_sl_no
        self.last_unpaid_age_idx = last_unpaid_age_idx


def __pay_counters(
        ages: List[AccountAge],
        amount: float,
        date: datetime,
        entry: JournalEntry,
        last_unpaid_age_idx
) -> Tuple[float, int]:
    if len(ages) == 0:
        return amount, last_unpaid_age_idx
    if amount == 0:
        return 0, last_unpaid_age_idx
    rem_amount = amount
    while rem_amount > 0 and last_unpaid_age_idx < len(ages):
        _, rem_amount = ages[last_unpaid_age_idx].counter.pay(rem_amount, date, {'entry': entry.__dict__})
        if ages[last_unpaid_age_idx].counter.is_paid():
            last_unpaid_age_idx += 1
        else:
            break
    return rem_amount, last_unpaid_age_idx


def __update_account_aging(account_balance_type: str, entry: JournalEntry, aging: AccountAging):
    positive_amount = entry.cr_amount if account_balance_type == BalanceType.CREDIT.value else entry.dr_amount
    negative_amount = entry.dr_amount if account_balance_type == BalanceType.CREDIT.value else entry.cr_amount
    if positive_amount > 0:
        meta = re.match('.*##(.*)##.*', entry.narration)
        aging.ages.append(
            AccountAge(
                entry.date,
                AmountCounter(positive_amount),
                json.loads(meta.group(1)) if meta else None,
                entry
            )
        )
    aging.excess_amount, aging.last_unpaid_age_idx = __pay_counters(
        aging.ages,
        aging.excess_amount + negative_amount,
        entry.date,
        entry,
        aging.last_unpaid_age_idx
    )
    aging.last_sl_no = entry.sl_no


def get_account_aging(
        config: dict,
        entries: List[JournalEntry],
        account: str,
        as_of: datetime,
        previous_aging: AccountAging = None
) -> AccountAging:
    def should_entry_applied(e: JournalEntry) -> bool:
        return e.date <= as_of and e.account == account \
               and (previous_aging is None or e.sl_no > previous_aging.last_sl_no)

    aging = previous_aging
    if aging is None:
        aging = AccountAging(account, [], 0, -1)

    if aging.account != account:
        raise ValueError('Invalid previous aging! account not matching')

    account_type = config['accounts'][account]['type']
    account_balance_type = config['account_types'][account_type]['balance_type']
    for entry in entries:
        if not should_entry_applied(entry):
            continue
        __update_account_aging(account_balance_type, entry, aging)
    return aging


def get_accounts_aging(
        config: dict,
        entries: List[JournalEntry],
        accounts: List[str],
        as_of: datetime,
        previous_aging: Dict[str, AccountAging] = None
) -> Dict[str, AccountAging]:
    aging = previous_aging
    if aging is None:
        aging = {}
        for account in accounts:
            aging[account] = AccountAging(account, [], 0, -1)

    if not all([aging.get(acc) for acc in accounts]):
        raise ValueError('Invalid previous aging! accounts not matching')

    def should_entry_applied(entry: JournalEntry) -> bool:
        return entry.date <= as_of and aging.get(entry.account) is not None \
               and (previous_aging is None or entry.sl_no > previous_aging[entry.account].last_sl_no)

    entries = entries[max([aging.last_sl_no for aging in previous_aging.values()]) + 1:] if previous_aging else entries
    for entry in entries:
        if not should_entry_applied(entry):
            continue
        account_type = config['accounts'][entry.account]['type']
        account_balance_type = config['account_types'][account_type]['balance_type']
        __update_account_aging(account_balance_type, entry, aging[entry.account])
    return aging
