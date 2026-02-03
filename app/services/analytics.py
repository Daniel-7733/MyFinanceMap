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


MONEY_2DP: Decimal = Decimal("0.01")


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


def monthly_income_expense_series(transactions: Iterable[Transaction]) -> dict[str, list]:
    """
    Returns chart-ready data aligned by month:
    {
      "labels": ["2026-01", "2026-02"],
      "income": [3000.00, 2500.00],
      "expense": [1200.00, 1800.00]
    }
    """
    income_by_month: dict[str, Decimal] = defaultdict(Decimal)
    expense_by_month: dict[str, Decimal] = defaultdict(Decimal)

    for t in transactions:
        month_key = t.period_month.strftime("%Y-%m")  # consistent month axis
        if t.txn_type == "income":
            income_by_month[month_key] += (t.amount_home or Decimal("0"))
        elif t.txn_type == "expense":
            expense_by_month[month_key] += (t.amount_home or Decimal("0"))

    # union of months from both
    months = sorted(set(income_by_month.keys()) | set(expense_by_month.keys()))

    labels: list[str] = months
    income_series: list[float] = [
        float(income_by_month[m].quantize(MONEY_2DP)) for m in months
    ]
    expense_series: list[float] = [
        float(expense_by_month[m].quantize(MONEY_2DP)) for m in months
    ]

    return {"labels": labels, "income": income_series, "expense": expense_series}

