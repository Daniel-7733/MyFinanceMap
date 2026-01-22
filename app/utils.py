"""
                            *************************************

                            Useful helper functions (not belonging
                                 to any single feature/module)

                            *************************************
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from secrets import token_hex
from typing import TYPE_CHECKING, Iterable


if TYPE_CHECKING:
    from .models import Transaction


def generate_random_string(n_bytes: int = 32) -> str:
    """
    Generate a cryptographically strong random hex string.

    NOTE: token_hex(n_bytes) returns a string of length 2 * n_bytes characters.
    Example: n_bytes=32 -> 64 hex characters.
    """
    return token_hex(n_bytes)


def month_start(d: date) -> date:
    """
    Return the first day of the month for date d.
    Example: 2025-11-15 -> 2025-11-01
    """
    return date(d.year, d.month, 1)


def split_income_expense(transactions: Iterable["Transaction"]) -> tuple[list[Decimal], list[Decimal]]:
    """
    Split transactions into two lists: (incomes, expenses).
    :param transactions: transactions iterable
    :return: two lists: (incomes, expenses)
    """

    incomes: list[Decimal] = []
    expenses: list[Decimal] = []

    for t in transactions:
        if t.txn_type == "income":
            incomes.append(t.amount_home)
        elif t.txn_type == "expense":
            expenses.append(t.amount_home)

    return incomes, expenses


def get_available_months(transactions: Iterable["Transaction"]) -> dict[str, str]:
    """
    Returns dict mapping 'YYYY-MM' -> 'MonthName YYYY'
    Example: {'2025-11': 'November 2025'}
    """
    options: dict[str, str] = {}

    for t in transactions:
        pm: date = t.period_month  # use period_month (not date_paid)

        key: str = pm.strftime("%Y-%m")         # '2025-11'
        label: str = pm.strftime("%B %Y")       # 'November 2025'

        options[key] = label

    # Optional: sort by key (year-month)
    return dict(sorted(options.items()))


def get_current_month() -> tuple[str, str]:
    """
    Returns:
      - key:   "YYYY-MM"  (for <option value=""> and filtering)
      - label: "Month YYYY" (for showing to the user)
    """
    today: date = date.today()
    key: str = today.strftime("%Y-%m")      # "2026-01"
    label: str = today.strftime("%B %Y")    # "January 2026"
    return key, label

