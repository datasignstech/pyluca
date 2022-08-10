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


class PositiveEntry(NamedTuple):
    date: datetime
    counter: AmountCounter
    meta: Optional[dict]


def _pay_counters(positive_entries: List[PositiveEntry], amount: float, date: datetime) -> float:
    if len(positive_entries) == 0:
        return amount
    if amount == 0:
        return 0
    rem_amount, cur_idx = amount, 0
    while rem_amount > 0 and cur_idx < len(positive_entries):
        if not positive_entries[cur_idx].counter.is_paid():
            _, rem_amount = positive_entries[cur_idx].counter.pay(rem_amount, date)
        if positive_entries[cur_idx].counter.is_paid():
            cur_idx += 1
        else:
            break
    return rem_amount


def get_account_aging(
        config: dict,
        entries: List[JournalEntry],
        account: str,
        as_of: datetime
) -> List[AccountAge]:
    filtered_entries = [e for e in entries if e.date <= as_of and e.account == account]
    positive_entries: List[PositiveEntry] = []
    active_counter_idx, excess_amount = 0, 0
    account_type = config['accounts'][account]['type']
    for entry in filtered_entries:
        account_balance_type = config['account_types'][account_type]['balance_type']
        positive_amount = entry.cr_amount if account_balance_type == BalanceType.CREDIT.value else entry.dr_amount
        negative_amount = entry.dr_amount if account_balance_type == BalanceType.CREDIT.value else entry.cr_amount
        if positive_amount > 0:
            meta = re.match('.*##(.*)##.*', entry.narration)
            positive_entries.append(
                PositiveEntry(
                    entry.date,
                    AmountCounter(positive_amount),
                    json.loads(meta.group(1)) if meta else None
                )
            )
        excess_amount = _pay_counters(positive_entries, excess_amount + negative_amount, entry.date)
    return [AccountAge(entry.date, entry.counter, entry.meta) for entry in positive_entries]
