"""
                            *************************************

                            The brain of the app: budgeting logic
                                 money rules & calculations

                            *************************************
"""

from decimal import Decimal


MONEY_2DP: Decimal = Decimal("0.01")


def total_income(incomes: list[Decimal]) -> Decimal:
    """
    Calculate total income from a list of Decimal values.
    Safe even if the list is empty.
    """
    return sum(incomes, Decimal("0"))


def calculate_balance(incomes: list[Decimal], expenses: list[Decimal]) -> Decimal:
    """
    Remaining balance = total income - total expenses, rounded to 2 decimals.
    """
    balance: Decimal = sum(incomes, Decimal("0")) - sum(expenses, Decimal("0"))
    return balance.quantize(MONEY_2DP)


def calculate_503020(income: Decimal) -> dict[str, Decimal]:
    """
    50/30/20 budget distribution (money amounts, 2 decimals).
    """
    needs: Decimal = (income * Decimal("0.50")).quantize(MONEY_2DP)
    wants: Decimal = (income * Decimal("0.30")).quantize(MONEY_2DP)
    savings: Decimal = (income * Decimal("0.20")).quantize(MONEY_2DP)

    return {"needs": needs, "wants": wants, "savings": savings}
