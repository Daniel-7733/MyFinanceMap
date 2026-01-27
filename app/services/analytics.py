"""
                            *************************************

                            The brain of the app: analytics logic
                                 summaries, totals, trends

                            *************************************
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Iterable
from sqlalchemy import func, case
from ..models import Transaction, db
from collections import defaultdict


def monthly_totals(last_n: int = 6) -> list[dict[str, Any]]:
    """
    Return last_n months totals (income/expense/net) based on Transaction.period_month.
    Works well with SQLite.
    """
    # SQLite: date stored as YYYY-MM-DD; we group by YYYY-MM
    month_key = func.strftime("%Y-%m", Transaction.period_month)

    income_sum = func.coalesce(
        func.sum(
            case(
                (Transaction.txn_type == "income", Transaction.amount_home),
                else_=0,
            )
        ),
        0,
    )

    expense_sum = func.coalesce(
        func.sum(
            case(
                (Transaction.txn_type == "expense", Transaction.amount_home),
                else_=0,
            )
        ),
        0,
    )

    rows = (
        db.session.query(
            month_key.label("month"),
            income_sum.label("income"),
            expense_sum.label("expense"),
        )
        .group_by(month_key)
        .order_by(month_key.desc())
        .limit(last_n)
        .all()
    )

    # rows come newest -> oldest; charts usually want oldest -> newest
    rows = list(reversed(rows))

    data: list[dict[str, Any]] = []
    for r in rows:
        income = Decimal(str(r.income))
        expense = Decimal(str(r.expense))
        data.append(
            {
                "month": r.month,               # "2026-01"
                "income": float(income),
                "expense": float(expense),
                "net": float(income - expense),
            }
        )
    return data


def category_totals(transactions: Iterable["Transaction"], period_month: date) -> list[dict[str, Decimal]]:
    """
    Calculate total expense per category for a given month.

    Args:
        transactions: Iterable of Transaction objects.
        period_month: The month to filter by (stored as the first day of the month, e.g. date(2026, 1, 1)).

    Returns:
        A list of dicts like: {"category": "groceries", "total": Decimal("123.45")}, sorted by total desc.
    """


    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    for t in transactions:
        if t.period_month == period_month and t.txn_type == "expense":
            totals[t.category] += (t.amount_home or Decimal("0"))

    data: list[dict[str, str | Decimal]] = [{"category": cat, "total": total} for cat, total in totals.items()]
    data.sort(key=lambda x: x["total"], reverse=True)
    return data


