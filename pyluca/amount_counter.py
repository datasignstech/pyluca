from datetime import datetime
from abc import abstractmethod
from typing import List, Optional, Tuple


FLOATING_PRECISION = 1e-6


class AccountPayment:
    def __init__(self, amount: float, date: datetime):
        self.amount = amount
        self.date = date


class AccountWriterInterface:
    @abstractmethod
    def write(self, amount: float, date: datetime, due_date: datetime):
        pass


class AmountCounterInterface:
    @abstractmethod
    def pay(self, amount: float, date: datetime) -> Tuple[Optional[AccountPayment], float]:
        pass


class AmountCounter(AmountCounterInterface):
    def __init__(self, total_amount: float):
        assert total_amount > FLOATING_PRECISION, f'Cannot initiate AmountCounter with <= {FLOATING_PRECISION} amount'
        self.total_amount = total_amount
        self.paid_amount = 0
        self.payments: List[AccountPayment] = []

    def add(self, amount: float):
        self.total_amount += amount

    def pay(self, amount: float, date: datetime):
        if amount < 0:
            raise ValueError('Pay amount should not be less than 0')
        possible_pay_amount = min(self.get_balance(), amount)
        if possible_pay_amount > 0:
            payment = AccountPayment(possible_pay_amount, date)
            self.payments.append(payment)
            self.paid_amount += possible_pay_amount
            return payment, amount - possible_pay_amount
        return None, amount

    def get_balance(self):
        diff = self.total_amount - self.paid_amount
        return diff if diff > FLOATING_PRECISION else 0

    def is_paid(self):
        return abs(self.get_balance()) == 0

    def get_paid_date(self) -> Optional[datetime]:
        if self.is_paid():
            return self.payments[len(self.payments) - 1].date
        return None

    def get_paid_amount(self):
        return self.paid_amount
