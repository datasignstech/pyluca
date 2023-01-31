import json
import re
from copy import deepcopy
from datetime import datetime
from typing import NamedTuple, List, Optional, Tuple
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


class AgingState:
    def __init__(self, account: str, positive_entries: List[PositiveEntry], excess_amount: float, sl_no: int):
        self.account = account
        self.positive_entries = positive_entries
        self.excess_amount = excess_amount
        self.sl_no = sl_no


def __pay_counters(positive_entries: List[PositiveEntry], amount: float, date: datetime) -> float:
    if len(positive_entries) == 0:
        return amount
    if amount == 0:
        return 0
    rem_amount, cur_idx = amount, 0
    while rem_amount > 0 and cur_idx < len(positive_entries):
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
        as_of: datetime,
        previous_state: AgingState = None
) -> Tuple[List[AccountAge], AgingState]:
    def should_entry_applied(e: JournalEntry):
        return e.date <= as_of and e.account == account and (previous_state is None or e.sl_no > previous_state.sl_no)

    filtered_entries = [e for e in entries if should_entry_applied(e)]

    state = deepcopy(previous_state)
    if state is None:
        state = AgingState(account, [], 0, -1)

    if state.account != account:
        raise ValueError('Invalid previous state provided. account should match')

    account_type = config['accounts'][account]['type']
    for entry in filtered_entries:
        account_balance_type = config['account_types'][account_type]['balance_type']
        positive_amount = entry.cr_amount if account_balance_type == BalanceType.CREDIT.value else entry.dr_amount
        negative_amount = entry.dr_amount if account_balance_type == BalanceType.CREDIT.value else entry.cr_amount
        if positive_amount > 0:
            meta = re.match('.*##(.*)##.*', entry.narration)
            state.positive_entries.append(
                PositiveEntry(
                    entry.date,
                    AmountCounter(positive_amount),
                    json.loads(meta.group(1)) if meta else None
                )
            )
        state.excess_amount = __pay_counters(state.positive_entries, state.excess_amount + negative_amount, entry.date)
        state.sl_no = entry.sl_no
    return [AccountAge(entry.date, entry.counter, entry.meta) for entry in state.positive_entries], state
