import json
from typing import Union

from pyluca.account_config import Action, Operator
from pyluca.accountant import Accountant
from pyluca.ledger import Ledger
from pyluca.event import Event


_OPERATOR_CONFIG = {
    '*': lambda a, b: a * b,
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '/': lambda a, b: a / b,
    'min': lambda a, b: min(a, b),
    '==': lambda a, b: a == b,
    '!': lambda a, b: not a
}


def _apply_operator(operator: Operator, event: Event, accountant: Accountant):
    return _OPERATOR_CONFIG[operator.operator](
        _get_param(operator.a, event, accountant),
        _get_param(operator.b, event, accountant)
    )


def _get_param(
        key: Union[str, list, Operator],
        event: Event,
        accountant: Accountant
):
    if key is None:
        return None
    if type(key) in [int, float]:
        return key
    if isinstance(key, Operator):
        return _apply_operator(key, event, accountant)
    if key.startswith('str.'):
        return key.replace('str.', '')
    if key.startswith('balance.'):
        return Ledger(accountant.journal, accountant.config)\
            .get_account_balance(key.replace('balance.', ''))
    if hasattr(event, key):
        return event.__getattribute__(key)
    raise NotImplementedError(f'param {key} not implemented')


def _get_narration(action: Action, event: Event, accountant: Accountant):
    narration = action.narration
    if action.meta:
        meta = {k: _get_param(v, event, accountant) for k, v in action.meta.items()}
        narration = f'{narration} ##{json.dumps(meta)}##'
    return narration


def _apply_action(
        action: Action,
        event: Event,
        accountant: Accountant
):
    if action.iff and not _get_param(action.iff, event, accountant):
        return
    action_type = action.type if action.type else 'je'
    if action_type == 'je':
        accountant.enter_journal(
            action.dr_account,
            action.cr_account,
            _get_param(action.amount, event, accountant),
            event.date,
            _get_narration(action, event, accountant)
        )


def apply(event: Event, accountant: Accountant):
    event_config = accountant.config.actions_config.on_event[event.__class__.__name__]
    for action in event_config.actions:
        _apply_action(action, event, accountant)
