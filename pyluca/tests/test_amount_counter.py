from datetime import datetime
from unittest import TestCase

from pyluca.amount_counter import AmountCounter


class TestAmountCounter(TestCase):
    def test_amount_counter(self):
        counter = AmountCounter(1000, None)
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
        counter = AmountCounter(1000, None)
        counter.pay(33.3, datetime(2022, 4, 20))
        self.assertEqual(counter.get_balance(), 966.7)
        self.assertEqual(len(counter.payments), 1)
        self.assertEqual(counter.payments[0].amount, 33.3)
        self.assertEqual(counter.payments[0].date, datetime(2022, 4, 20))
        self.assertAlmostEqual(counter.pay(1000, datetime(2022, 4, 30))[1], 33.3)
