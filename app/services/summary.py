from decimal import Decimal
from .budgeting import calculate_balance
from ..utils import split_income_expense
from ..models import Transaction
from .budgeting import available_balance, deficit_amount
from typing import Iterable


def get_balance(transactions) -> Decimal:
    """
    This function will calculate the balance from the transactions

    :param transactions: List of transactions
    :param transactions: A list of transactions of class Transaction
    :return: Balance of user
    """
    incomes, expenses = split_income_expense(transactions)
    return calculate_balance(incomes, expenses)


def get_finance_overview() -> tuple[list[Transaction], Decimal, Decimal, Decimal]:
    """
    This function will calculate the finance overview (like balance, available, and deficit)
    from the transactions and give a list of transactions.

    Returns: Finance overview as a tuple:
      - transactions,
      - balance,
      - available_balance,
      - deficit_amount
    """

    transactions: list[Transaction] = Transaction.query.order_by(Transaction.id.desc()).all()
    balance: Decimal = get_balance(transactions)
    available: Decimal = available_balance(balance)
    deficit: Decimal = deficit_amount(balance)

    return transactions, balance, available, deficit


def get_income_expense_net(transactions: Iterable["Transaction"]) -> tuple[Decimal, Decimal, Decimal]:
    """
    Split transactions into three type of amount: (income, expense, save).
    :param transactions: transactions iterable
    :return: three type of amount: (income, expense, save)
    """
    income_total = Decimal("0.00")
    expense_total = Decimal("0.00")

    for t in transactions:
        amt = t.amount_home or Decimal("0.00")
        if t.txn_type == "income":
            income_total += amt
        elif t.txn_type == "expense":
            expense_total += amt

    net = income_total - expense_total
    return income_total, expense_total, net

