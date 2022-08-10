from decimal import Decimal, ROUND_UP


PRECISION_ROUND_OFF_DECIMAL_POINTS = 6
PRECISION_IS_PAID_DECIMAL_POINTS = 4


def round_off_amount(amount: float):
    max_precision = 10**PRECISION_ROUND_OFF_DECIMAL_POINTS
    if amount - (int((amount * max_precision)) / max_precision) > 0:
        return float(Decimal(amount).quantize(Decimal('.' + str(int(max_precision))[::-1]), rounding=ROUND_UP))
    return amount


def zeroed(amount: float):
    max_float = (1 / (10**PRECISION_IS_PAID_DECIMAL_POINTS))
    min_float = -1 * max_float
    if min_float < amount < max_float:
        return 0
    return amount
