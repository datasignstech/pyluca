import pandas as pd
from account_config import AccountingConfig


def add_account_balance(config: AccountingConfig, ledger: pd.DataFrame, account: str) -> pd.DataFrame:
    account_type = config.ACCOUNTS[account].type
    positive_col, negative_col = 'cr_amount', 'dr_amount'
    if account_type in config.DEBIT_BALANCE_ACCOUNT_TYPES:
        positive_col, negative_col = 'dr_amount', 'cr_amount'

    balance, balances = 0, []
    for i, row in ledger.iterrows():
        if row['account'] == account:
            balance += row[positive_col]
            balance -= row[negative_col]
        balances.append(balance)
    ledger[account] = balances
    return ledger
