from datetime import datetime
from unittest import TestCase

from pyluca.amount_counter import AmountCounter, is_amount_counter_paid, get_amount_counter_paid_date


class TestAmountCounter(TestCase):
    def test_amount_counter(self):
        counter = AmountCounter(1000)
        now = datetime.now()
        self.assertEqual(counter.pay(0, now)[1], 0)
        self.assertEqual(counter.pay(5, now)[1], 0)
        self.assertEqual(counter.get_balance(), 995)
        self.assertEqual(counter.pay(1000, now)[1], 5)
        self.assertEqual(counter.get_balance(), 0)
        self.assertTrue(is_amount_counter_paid(counter))

    def test_payments(self):
        counter = AmountCounter(1000)
        counter.pay(33.3, datetime(2022, 4, 20))
        self.assertEqual(counter.get_balance(), 966.7)
        self.assertEqual(len(counter.payments), 1)
        self.assertEqual(counter.payments[0].amount, 33.3)
        self.assertEqual(counter.payments[0].date, datetime(2022, 4, 20))
        self.assertEqual(get_amount_counter_paid_date(counter, None), None)
        self.assertAlmostEqual(counter.pay(1000, datetime(2022, 4, 30))[1], 33.3)
        self.assertEqual(get_amount_counter_paid_date(counter, None), datetime(2022, 4, 30))

    def test_floating_precision(self):
        ac = AmountCounter(100 + 1e-8)
        ac.pay(100, datetime(2022, 8, 10))
        self.assertTrue(is_amount_counter_paid(ac))
        self.assertNotEqual(ac.get_balance(), 0)
        self.assertTrue(1e-8 > ac.get_balance() < 1)
        self.assertEqual(ac.paid_amount, 100)
