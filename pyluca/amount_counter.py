from datetime import datetime
from abc import abstractmethod
from typing import List, Optional, Tuple


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
        self.total_amount = total_amount
        self.paid_amount = 0
        self.payments: List[AccountPayment] = []

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
        return self.total_amount - self.paid_amount


def is_amount_counter_paid(counter: AmountCounter):
    return abs(counter.get_balance()) < 1e-3


def get_amount_counter_paid_date(counter: AmountCounter, due_date: datetime = None) -> Optional[datetime]:
    if is_amount_counter_paid(counter):
        if len(counter.payments) == 0:
            return due_date
        return counter.payments[len(counter.payments) - 1].date
    return None
