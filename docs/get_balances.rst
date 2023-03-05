Get balances
============

One of the common functionality that we would like to apply on DEAS is to get balance of an account. :class:`~pyluca.ledger.Ledger` provides handy functions which are aggregations on a :class:`~pyluca.journal.Journal`. Following is an example

.. code-block:: python

   import Journal, Accountant, Ledger from pyluca

   journal = Journal()
   config = {...}
   accountant = Accountant(journal, config)
   accountant.enter_journal(
      dr_account='SAVINGS_BANK',
      cr_account='SALARY',
      amount=20000,
      date=datetime(2022, 4, 30),
      narration='March salary'
   )

   ledger = Ledger(journal, config)
   print(ledger.get_account_balance('SAVINGS_BANK')) # 20000


:class:`~pyluca.ledger.Ledger` takes care of the account type and does the calculation accordingly