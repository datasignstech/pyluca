import pandas as pd
from pyluca.account_config import BalanceType


def add_account_balance(config: dict, ledger: pd.DataFrame, account: str) -> pd.DataFrame:
    account_type = config['accounts'][account]['type']
    positive_col, negative_col = 'cr_amount', 'dr_amount'
    if config['account_types'][account_type]['balance_type'] == BalanceType.DEBIT.value:
        positive_col, negative_col = 'dr_amount', 'cr_amount'

    balance, balances = 0, []
    for i, row in ledger.iterrows():
        if row['account'] == account:
            balance += row[positive_col]
            balance -= row[negative_col]
        balances.append(balance)
    ledger[account] = balances
    return ledger
