from datetime import datetime
from random import randint
from unittest import TestCase

from pyluca.amount_counter import AmountCounter
from pyluca.round_off import round_off_amount, zeroed


class TestRoundOff(TestCase):
    def test_round_off(self):
        self.assertEqual(round_off_amount(1000), 1000)
        self.assertEqual(round_off_amount(1000.0), 1000)
        self.assertNotEqual(round_off_amount(1000.01), 1000)
        self.assertEqual(round_off_amount(1000.01), 1000.01)
        self.assertEqual(round_off_amount(1000.001), 1000.001)
        self.assertEqual(round_off_amount(1000.0001), 1000.0001)
        self.assertEqual(round_off_amount(1000.00001), 1000.00001)
        self.assertEqual(round_off_amount(1000.000001), 1000.000001)
        self.assertEqual(round_off_amount(1000.0000001), 1000.000001)
        self.assertNotEqual(round_off_amount(1000.00000001), 1000.00000001)
        self.assertEqual(round_off_amount(1000.00000001), 1000.000001)
        self.assertEqual(round_off_amount(1000.0000019398493849898928), 1000.000002)
        self.assertEqual(round_off_amount(1000.000001999999), 1000.000002)
        self.assertEqual(round_off_amount(1000.000001999999999999999999999999), 1000.000002)

        self.assertEqual(round_off_amount(1000.0000010001), 1000.000002)
        self.assertEqual(round_off_amount(1000.00000100001), 1000.000002)
        self.assertEqual(round_off_amount(1000.000001000001), 1000.000002)

        # weired
        self.assertEqual(round_off_amount(1000.000001000000000000000000001), 1000.000001)

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
        self.assertEqual(zeroed(0.00001), 0.00001)
        self.assertEqual(zeroed(0.0001), 0.0001)
        self.assertEqual(zeroed(0.001), 0.001)
        self.assertEqual(zeroed(0.01), 0.01)
        self.assertEqual(zeroed(0.1), 0.1)
        self.assertEqual(zeroed(-0.00001), -0.00001)
        self.assertEqual(zeroed(-0.000001), -0.000001)

    def test_with_amount_counter(self):
        ac = AmountCounter(100)
        ac.pay(99, datetime(2022, 8, 10))
        self.assertEqual(ac.get_balance(), 1)
        p1, p2 = .9999938838883, .000006
        self.assertNotEqual(p1 + p2, 0)
        ac.pay(p1, datetime(2022, 8, 10))
        self.assertFalse(ac.is_paid())
        ac.pay(p2, datetime(2022, 8, 10))
        self.assertTrue(ac.is_paid())
