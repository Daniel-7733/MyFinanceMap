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


def split_amounts_by_type(transactions: Iterable["Transaction"]) -> tuple[list[Decimal], list[Decimal]]:
    """
    Split transactions into two lists: (incomes, expenses).
    """
    incomes: list[Decimal] = []
    expenses: list[Decimal] = []

    for t in transactions:
        if t.txn_type == "income":
            incomes.append(t.amount)
        elif t.txn_type == "expense":
            expenses.append(t.amount)

    return incomes, expenses

