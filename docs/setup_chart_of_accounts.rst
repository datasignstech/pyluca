Setup Chart of Accounts
========================

After setting up the types of accounts, we need to setup th chart of accounts that is specific to the business. This purely depends on the requirement from the finance perspective.

To demonstrate, we will be setting up accounts for personal finance management. We will add *accounts* in the config we built in the previous section

.. code-block:: python

   config = {
      'account_types': ...,
      'accounts': {
        'SALARY': {'type': 'INCOME'},
        'SAVINGS_BANK': {'type': 'ASSET'},
        'MUTUAL_FUNDS': {'type': 'ASSET'},
        'LOANS': {'type': 'ASSET'},
        'CAR_EMI': {'type': 'EXPENSE'}
      }
   }

It is recommended to maintain this config as a *json* instead of python dict so that the configuration is plain text but not any computation.