from datetime import datetime
from random import randint
from unittest import TestCase

from pyluca.amount_counter import AmountCounter
from pyluca.round_off import zeroed


class TestRoundOff(TestCase):
    def test_zeroed(self):
        self.assertEqual(zeroed(0), 0)
        self.assertEqual(zeroed(1), 1)
        for i in range(100):
            num = randint(-10000000000, 10000000000)
            self.assertEqual(zeroed(num), num)
        self.assertEqual(zeroed(0.00000000000000001), 0)
        self.assertEqual(zeroed(0.000000000000001), 0)
        self.assertEqual(zeroed(0.0000000000001), 0)
        self.assertEqual(zeroed(0.00000000001), 0)
        self.assertEqual(zeroed(0.000000001), 0)
        self.assertEqual(zeroed(0.0000001), 0)
        self.assertEqual(zeroed(0.00001), 0)
        self.assertEqual(zeroed(0.0001), 0)
        self.assertEqual(zeroed(0.001), 0.001)
        self.assertEqual(zeroed(0.01), 0.01)
        self.assertEqual(zeroed(0.1), 0.1)
        self.assertEqual(zeroed(-0.1), -0.1)
        self.assertEqual(zeroed(-0.01), -0.01)
        self.assertEqual(zeroed(-0.001), -0.001)
        self.assertEqual(zeroed(-0.0001), 0)
        self.assertEqual(zeroed(-0.00001), 0)
        self.assertEqual(zeroed(-0.000001), 0)

        self.assertEqual(zeroed(0.0009999999999999999), 0)
        # weird
        self.assertEqual(zeroed(0.00099999999999999999), 0.001)

    def test_with_amount_counter(self):
        ac = AmountCounter(100)
        ac.pay(99, datetime(2022, 8, 10))
        self.assertEqual(ac.get_balance(), 1)
        p1, p2 = .9938838883, .006
        self.assertNotEqual(p1 + p2, 0)
        ac.pay(p1, datetime(2022, 8, 10))
        self.assertFalse(ac.is_paid())
        ac.pay(p2, datetime(2022, 8, 10))
        self.assertTrue(ac.is_paid())
