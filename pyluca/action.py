import re
import json
from typing import Union
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


def _apply_operator(operator: dict, event: Event, accountant: Accountant, context: dict):
    return _OPERATOR_CONFIG[operator['type']](
        _get_param(operator['a'], event, accountant, context),
        _get_param(operator.get('b'), event, accountant, context)
    )


def _get_param(
        key: Union[str, list, dict],
        event: Event,
        accountant: Accountant,
        context: dict
):
    if key is None:
        return None
    if type(key) in [int, float]:
        return key
    if isinstance(key, dict) and key.get('type'):
        return _apply_operator(key, event, accountant, context)
    if key.startswith('str.'):
        return key.replace('str.', '')
    if key.startswith('context.'):
        next_key = key.replace('context.', '')
        return _get_param(context[next_key], event, accountant, context)
    if key.startswith('balance.'):
        return Ledger(accountant.journal, accountant.config).get_account_balance(key.replace('balance.', ''))
    if hasattr(event, key):
        return event.__getattribute__(key)
    return key


def _parse_narration(narration: str, event: Event, accountant: Accountant, context: dict):
    matches = re.findall("\{([^}]+)\}", narration)
    if matches:
        for match in matches:
            narration = re.sub(match, _get_param(match, event, accountant, context), narration)
        narration = re.sub(r'[{}]', '', narration)
    return narration


def _get_narration(action: dict, event: Event, accountant: Accountant, context: dict):
    narration = _parse_narration(action['narration'], event, accountant, context)
    if action.get('meta'):
        meta = {k: _get_param(v, event, accountant, context) for k, v in action['meta'].items()}
        narration = f'{narration} ##{json.dumps(meta)}##'
    return narration


def _apply_action(
        action: dict,
        event: Event,
        accountant: Accountant,
        context: dict,
        common_actions: dict
):
    if action.get('iff') and not _get_param(action['iff'], event, accountant, context):
        return
    action_type = action.get('type', 'je')
    if action_type == 'je':
        accountant.enter_journal(
            action['dr_account'],
            action['cr_account'],
            _get_param(action['amount'], event, accountant, context),
            event.date,
            _get_narration(action, event, accountant, context)
        )
    elif action_type.startswith('action.'):
        for sub_action in common_actions[action_type.replace('action.', '')]['actions']:
            _apply_action(sub_action, event, accountant, {**context, **action.get('context', {})}, common_actions)


def apply(event: Event, accountant: Accountant, context: dict = None):
    context = context if context else {}
    event_config = accountant.config['actions_config']['on_event'][event.__class__.__name__]
    common_actions = accountant.config['actions_config'].get('common_actions', {})
    for action in event_config['actions']:
        _apply_action(action, event, accountant, context, common_actions)
