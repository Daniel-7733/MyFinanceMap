from decimal import Decimal


def statistics(amounts: list[Decimal]) -> dict[str, Decimal]:
    """
    Function to calculate the expense statistics. Note: if the amount is empty, the function return 0 for all
    maximum, minimum, and average.
    :param amounts: (Decimal) a list of amount.
    :return: maximum, minimum, and average amount.
    """
    zero = Decimal("0")

    if not amounts:
        return {
            "min": zero,
            "max": zero,
            "average": zero,
        }

    total_expense: Decimal = sum(amounts)
    count: Decimal = Decimal(len(amounts))

    return {
        "min": min(amounts),
        "max": max(amounts),
        "average": total_expense / count,
    }
