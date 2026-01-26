"""
                            *************************************

                            The brain of the app: analytics logic
                                 summaries, totals, trends

                            *************************************
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from sqlalchemy import func, case
from ..models import Transaction, db



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


def category_totals(period_month) -> list[dict]:
    ...

