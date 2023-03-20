Setup Accounting Config
========================

First step in the process is to setup the very basic accounting. There are four types of accounts

1. ASSET - Debit type

2. EXPENSE - Debit type

3. INCOME - Credit type

4. LIABILITY - Credit type

We need to set this up in a config dict which will be later used to pass the journal entries or anything else for that matter.

.. code-block:: python

   config = {
     'account_types': {
       'ASSET': {
         'balance_type': 'DEBIT'
       },
       'EXPENSE': {
         'balance_type': 'DEBIT'
       },
       'LIABILITY': {
         'balance_type': 'CREDIT'
       },
       'INCOME': {
         'balance_type': 'CREDIT'
       }
     }
   }


We will be carrying forward this config in the next section