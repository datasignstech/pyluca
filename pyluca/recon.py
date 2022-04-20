import datetime
from pyluca.account_config import AccountingConfig
from pyluca.accountant import Accountant
from pyluca.journal import Journal
from pyluca.ledger import Ledger


def _is_matching(config: AccountingConfig, journal_1: Journal, journal_2: Journal) -> bool:
    for acct_name in config.accounts.keys():
        if Ledger(journal_1, config).get_account_balance(acct_name) \
                != Ledger(journal_2, config).get_account_balance(acct_name):
            return False
    if Ledger(journal_1, config).get_account_balance('RECONCILE_CONTROL') != 0:
        return False
    if Ledger(journal_2, config).get_account_balance('RECONCILE_CONTROL') != 0:
        return False
    return True


def reconcile_ledger(
        config: AccountingConfig,
        closed_accountant: Accountant,
        current_accountant: Accountant,
        date: datetime.datetime
):
    assert _is_matching(config, closed_accountant.journal, current_accountant.journal) is False
    for acct_name in [a for a in config.accounts.keys() if a not in ['RECONCILE_CONTROL']]:
        diff = Ledger(current_accountant.journal, config).get_account_balance(acct_name) \
               - Ledger(closed_accountant.journal, config).get_account_balance(acct_name)
        if diff == 0:
            continue
        if config.accounts[acct_name].type in config.debit_balance_account_types:
            closed_accountant.adjust(acct_name, 'RECONCILE_CONTROL', diff, date)
        else:
            closed_accountant.adjust('RECONCILE_CONTROL', acct_name, diff, date)
    assert _is_matching(config, closed_accountant.journal, current_accountant.journal) is True
