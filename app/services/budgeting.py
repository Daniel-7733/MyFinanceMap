"""
                            *************************************

                            The brain of the app: budgeting logic
                                 money rules & calculations

                            *************************************
"""

from decimal import Decimal
from app.constants import MONEY_2DP



def total_income(incomes: list[Decimal]) -> Decimal:
    """
    Calculate total income from a list of Decimal values.
    Safe even if the list is empty.
    """
    return sum(incomes, Decimal("0"))

def total_expense(expenses: list[Decimal]) -> Decimal: # This is duplicate and I might delete it in future
    """
    Calculate total expense from a list of Decimal values.
    Safe even if the list is empty.
    """
    return sum(expenses, Decimal("0"))


def calculate_balance(incomes: list[Decimal], expenses: list[Decimal]) -> Decimal:
    """
    Remaining balance = total income - total expenses, rounded to 2 decimals.
    """
    balance: Decimal = sum(incomes, Decimal("0")) - sum(expenses, Decimal("0"))
    return balance.quantize(MONEY_2DP)


def available_balance(balance: Decimal) -> Decimal:
    """
    Calculate available balance.
    This function always return the bigger number by comparing the amount by zero;
    Otherwise, return 0, if the bigger number is zero.Example:
    max(-1, 0) -> 0
    max(1, 0) -> 1

    :param balance: balance or the amount.
    :return: available balance.
    """
    return max(balance, Decimal("0.00"))


def deficit_amount(balance: Decimal) -> Decimal:
    """
    Calculate deficit amount.
    This function always return the smaller number (negative number) by comparing the amount by zero;
    Otherwise, return 0, if the smaller number is bigger than zero.
    Example:
        >>> min(-1, 0) -> -1
        >>> min(1, 0) -> 0

    Note: The output always show the positive.
    Example:
        >>> min(-1, 0) -> -1 => abs(-1) -> 1
        >>> min(1, 0) -> 0; => abs(0) -> 0

    :param balance: balance or the amount.
    :return: available deficit.
    """
    return abs(min(balance, Decimal("0.00")))


def calculate_503020(income: Decimal) -> dict[str, Decimal]:
    """
    50/30/20 budget distribution (money amounts, 2 decimals).
    """
    needs: Decimal = (income * Decimal("0.50")).quantize(MONEY_2DP)
    wants: Decimal = (income * Decimal("0.30")).quantize(MONEY_2DP)
    savings: Decimal = (income * Decimal("0.20")).quantize(MONEY_2DP)

    return {"needs": needs, "wants": wants, "savings": savings}
