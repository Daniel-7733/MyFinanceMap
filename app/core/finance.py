from decimal import Decimal
from app.constants import MONEY_2DP


def compute_home_amount(amount: Decimal, currency: str, rate: Decimal | None, main_currency: str) -> Decimal:
    """
    Convert amount to home currency.

    - If currency == main_currency → return amount.
    - If foreign → rate must be provided.
    """
    if currency == main_currency:
        return amount
    if not rate:
        raise ValueError("Rate required for foreign currency")
    return (amount * rate).quantize(MONEY_2DP)


def percent(part: Decimal, whole: Decimal) -> Decimal:
    if whole == 0:
        return Decimal("0")
    return (part / whole) * Decimal("100")