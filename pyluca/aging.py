import json
import re
from datetime import datetime
from typing import NamedTuple, List, Optional
from pyluca.account_config import BalanceType
from pyluca.journal import JournalEntry
from pyluca.amount_counter import AmountCounter


class AccountAge(NamedTuple):
    date: datetime
    counter: AmountCounter
    meta: Optional[dict]
    je: JournalEntry


class AccountAging:
    def __init__(self, account: str, ages: List[AccountAge], excess_amount: float, last_sl_no: int):
        self.account = account
        self.ages = ages
        self.excess_amount = excess_amount
        self.last_sl_no = last_sl_no


def __pay_counters(ages: List[AccountAge], amount: float, date: datetime) -> float:
    if len(ages) == 0:
        return amount
    if amount == 0:
        return 0
    rem_amount, cur_idx = amount, 0
    while rem_amount > 0 and cur_idx < len(ages):
        _, rem_amount = ages[cur_idx].counter.pay(rem_amount, date)
        if ages[cur_idx].counter.is_paid():
            cur_idx += 1
        else:
            break
    return rem_amount


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
    for entry in entries:
        if not should_entry_applied(entry):
            continue
        account_balance_type = config['account_types'][account_type]['balance_type']
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
        aging.excess_amount = __pay_counters(aging.ages, aging.excess_amount + negative_amount, entry.date)
        aging.last_sl_no = entry.sl_no
    return aging
