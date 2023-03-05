Pass Journal Entries
====================

Once we have the *config* ready, we are all set to start passing the journal entries. To pass the journal entries, we need

1. A :class:`~pyluca.journal.Journal` on which the entries are added as a sequence ordered by date

2. A :class:`~pyluca.accountant.Accountant` which takes the Journal and config

Here is the example

.. code-block:: python

   import Journal, Accountant from pyluca

   journal = Journal()
   config = {...}
   accountant = Accountant(journal, config, key='user_1') # key will be passed to journal entries so that they can be grouped
   accountant.enter_journal(
      dr_account='SAVINGS_BANK',
      cr_account='SALARY',
      amount=20000,
      date=datetime(2022, 4, 30),
      narration='March salary'
   )

We successfully entered our first journal entry. Accountant maintains a serial number for each entry. You cannot enter back dated entries