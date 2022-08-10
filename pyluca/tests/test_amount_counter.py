from datetime import datetime
from unittest import TestCase

from pyluca.amount_counter import AmountCounter


class TestAmountCounter(TestCase):
    def test_amount_counter(self):
        counter = AmountCounter(1000)
        now = datetime.now()
        self.assertEqual(counter.pay(0, now)[1], 0)
        self.assertEqual(counter.pay(5, now)[1], 0)
        self.assertEqual(counter.get_balance(), 995)
        self.assertEqual(counter.pay(1000, now)[1], 5)
        self.assertEqual(counter.get_balance(), 0)
        self.assertTrue(counter.is_paid())
        counter.add(20)
        self.assertFalse(counter.is_paid())
        self.assertTrue(counter.get_balance(), 20)
        self.assertEqual(counter.pay(10, now)[1], 0)
        self.assertEqual(counter.pay(100, now)[1], 90)
        self.assertTrue(counter.is_paid())

    def test_payments(self):
        counter = AmountCounter(1000)
        counter.pay(33.3, datetime(2022, 4, 20))
        self.assertEqual(counter.get_balance(), 966.7)
        self.assertEqual(len(counter.payments), 1)
        self.assertEqual(counter.payments[0].amount, 33.3)
        self.assertEqual(counter.payments[0].date, datetime(2022, 4, 20))
        self.assertEqual(counter.get_paid_date(), None)
        self.assertAlmostEqual(counter.pay(1000, datetime(2022, 4, 30))[1], 33.3)
        self.assertEqual(counter.get_paid_date(), datetime(2022, 4, 30))

    def test_floating_precision(self):
        try:
            AmountCounter(1e-6)
            raise ValueError('AmountCounter should not be created with 1e-6')
        except AssertionError:
            pass
        ac = AmountCounter(100 + 1e-8)
        ac.pay(100, datetime(2022, 8, 10))
        self.assertTrue(ac.is_paid())
        self.assertEqual(ac.get_balance(), 0)
        self.assertEqual(ac.get_paid_amount(), 100)
