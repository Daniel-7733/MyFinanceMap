"""
                            *************************************

                            The brain of the app: budgeting logic
                                 money rules & calculations

                            *************************************
"""
# TODO: Note-> Decimal accept string as argument not int or float type. EX -> income = Decimal("3000")
from decimal import Decimal, getcontext

getcontext().prec = 28  # Optional: global precision


def total_income(incomes: list[Decimal]) -> Decimal:
    """Calculate the total income from a list of income values."""
    return sum(incomes)


# def add_transaction() -> int: This need modification
#     total: int = sum(transaction.amount for transaction in transactions)
#     return total


def calculate_balance(total_income_: Decimal, total_expenses: Decimal) -> Decimal:
    """Return the remaining balance after subtracting total expenses from total income."""
    return total_income_ - total_expenses


def calculate_503020(income: Decimal) -> dict[str, Decimal]:
    """Calculate 50/30/20 budget distribution based on income."""
    return {
        "needs": income * Decimal('0.50'),
        "wants": income * Decimal('0.30'),
        "savings": income * Decimal('0.20'),
    }
