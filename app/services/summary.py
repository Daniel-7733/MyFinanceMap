from decimal import Decimal
from .budgeting import calculate_balance
from ..utils import split_amounts_by_type
from ..models import Transaction
from .budgeting import available_balance, deficit_amount


def get_balance(transactions) -> Decimal:
    """
    This function will calculate the balance from the transactions

    :param transactions: List of transactions
    :param transactions: A list of transactions of class Transaction
    :return: Balance of user
    """
    incomes, expenses = split_amounts_by_type(transactions)
    return calculate_balance(incomes, expenses)


def get_finance_overview() -> tuple[list[Transaction], Decimal, Decimal, Decimal]:
    transactions: list[Transaction] = Transaction.query.order_by(Transaction.id.desc()).all()
    balance: Decimal = get_balance(transactions)
    available: Decimal = available_balance(balance)
    deficit: Decimal = deficit_amount(balance)
    return transactions, balance, available, deficit

