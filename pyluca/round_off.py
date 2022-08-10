PRECISION_ZERO = 3


def zeroed(amount: float):
    max_float = (1 / (10 ** PRECISION_ZERO))
    min_float = -1 * max_float
    if min_float < amount < max_float:
        return 0
    return amount
