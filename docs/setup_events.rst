Setup Events
=============

Writing custom :meth:`~pyluca.accountant.Accountant.enter_journal()` will grow out of control once we have multiple types of journal entries. Which will ultimately lead to confusion if we don't group them correctly and maintain.

In real world, the journal entries are not the direct actions/events that happen. They are **results** of real world **events**. Taking inspiration from this analogy, pyluca supports configuring different types of :class:`~pyluca.event.Event`.

Separately, you can configure a set of journal entries to be passed for each type of event.

Let us understand it from an example

.. code-block:: python

   import Event from pyluca

   class AmountEvent(Event):
       """
       An abstract Event which contains amount in it.
       Every event contains date at which it occurred
       """
       def __init__(
               self,
               event_id: str,
               amount: float,
               date: datetime,
               created_date: datetime,
               created_by: str = None
       ):
           self.amount = amount
           super(AmountEvent, self).__init__(event_id, date, created_date, created_by)


   class SalaryEvent(AmountEvent):
       pass


   class InvestMutualFundEvent(AmountEvent):
       pass


   class LendEvent(AmountEvent):
       pass


   class CollectionEvent(AmountEvent):
       pass


We just setup the events that happen in the real world. They are more intuitive to understand. Now we will configure the journal entries to be passed for each type of event. We just append following config to the existing config


.. code-block:: python

   config_dict = {
       ... # config as explained in previous sections
       'actions_config': {
           'on_event': {
               'SalaryEvent': {
                   'actions': [
                       {
                           'dr_account': 'SAVINGS_BANK',
                           'cr_account': 'SALARY',
                           'amount': 'amount',
                           'narration': 'Salary credit'
                       }
                   ]
               },
               'InvestMutualFundEvent': {
                   'actions': [
                       {
                           'dr_account': 'MUTUAL_FUNDS',
                           'cr_account': 'SAVINGS_BANK',
                           'amount': 'amount',
                           'narration': 'Invest in mutual funds'
                       }
                   ]
               },
               'LendEvent': {
                   'actions': [
                       {
                           'dr_account': 'LOANS',
                           'cr_account': 'SAVINGS_BANK',
                           'amount': 'amount',
                           'narration': 'Lend'
                       }
                   ]
               },
               'CollectionEvent': {
                   'actions': [
                       {
                           'dr_account': 'SAVINGS_BANK',
                           'cr_account': 'LOANS',
                           'amount': 'amount',
                           'narration': 'Collection for the loan'
                       }
                   ]
               }
           }
       }
   }


We are all set to construct the events and apply them. This can be done by :meth:`~pyluca.action.apply()` method as below

.. code-block:: python

   events = [
       SalaryEvent('salary', 20000, datetime(2022, 4, 30), datetime(2022, 4, 30)),
       InvestMutualFundEvent('mf-1', 10000, datetime(2022, 5, 2), datetime(2022, 5, 2)),
       LendEvent('lend-1', 5000, datetime(2022, 5, 4), datetime(2022, 5, 4))
   ]

   accountant = Accountant(Journal(), config_dict, 'person-1')
   for event in events:
       apply(event, accountant)

We just apply the event whenever it happens and the result would be

.. code-block:: python

   ledger = Ledger(accountant.journal, accountant.config)

   assert ledger.get_account_balance('SALARY') == 20000
   assert ledger.get_account_balance('MUTUAL_FUNDS') == 10000
   assert ledger.get_account_balance('LOANS') == 5000

This is more close to the real-world. In simple words, events turned into journal entries!