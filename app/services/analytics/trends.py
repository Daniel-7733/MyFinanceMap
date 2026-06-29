from decimal import Decimal


def percentage_change(old: Decimal, new: Decimal) -> Decimal:
    """
    Calculate the percentage change from an old value to a new value.

    Returns 0 if the old value is zero to prevent division by zero errors.

    :param old: The original or baseline financial value.
    :param new: The updated or current financial value.
    :return: The percentage increase or decrease relative to the old value.
    """
    if old == 0:
        return Decimal("0")
    return ((new - old) / abs(old)) * Decimal("100")


def difference(first: Decimal, second: Decimal) -> Decimal:
    """
    Calculate the absolute numerical difference between two values.

    Subtracts the first value from the second value to show direction.

    :param first: The initial or baseline value.
    :param second: The target or comparison value.
    :return: The net change resulting from subtracting first from second.
    """
    return second - first


def trend_direction(values: list[Decimal]) -> str:
    """
    Q: What direction am I moving?

    last value > first value  → improving
    last value < first value  → declining
    same                      → stable

    :param values: (list[Decimal]) List of amounts in months
    :return: improving, declining, or stable
    """
    if len(values) < 2:
        return "Not enough data"

    change = percentage_change(values[0], values[-1])

    if change >= Decimal("20"):
        return "Strongly Improving"
    elif change >= Decimal("5"):
        return "Slightly Improving"
    elif change <= Decimal("-20"):
        return "Strongly Declining"
    elif change <= Decimal("-5"):
        return "Slightly Declining"
    else:
        return "Stable"

