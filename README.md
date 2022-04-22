# pyluca
A headless python double entry accounting package. It is python Luca Pacioli :) 
It is a plug and play python module, which does NOT come with any server or databases.
It helps you to build your own application using core double entry accounting (pyluca)
module.

## Usage
On a high level, you just need to do following steps to start using it.
1. Setup accounting configuration
2. Pass journal entries
3. Get balances

## Example
**You need to have basic accounting/bookkeeping knowledge to set up the configuration**

Checkout out `demo/` for examples. You can event checkout `pyluca/tests` for advance usages.
1. Basic accounting configuration - `demo/personal_finance.py`
2. Creating an accountant and passing journal entries - `demo/personal_finance.py`
3. Creating events and configuring actions - `demo/personal_finance.py`
4. Ledger usage and as of any "time" - `demo/personal_finance.py` 
