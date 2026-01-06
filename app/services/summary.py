from decimal import Decimal
from .budgeting import calculate_balance
from ..utils import split_amounts_by_type


def get_balance(transactions) -> Decimal:
    """
    This function will calculate the balance from the transactions

    :param transactions: List of transactions
    :param transactions: A list of transactions of class Transaction
    :return: Balance of user
    """
    incomes, expenses = split_amounts_by_type(transactions)
    return calculate_balance(incomes, expenses)
