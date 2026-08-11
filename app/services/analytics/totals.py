from __future__ import annotations
from decimal import Decimal
from datetime import date
from typing import Iterable
from sqlalchemy import func, case
from ...models import Transaction, db
from collections import defaultdict
from app.constants import CATEGORY_BUCKETS
from .models import MonthlyTotalRow


def monthly_totals(user_id: int, last_n: int = 6) -> list[MonthlyTotalRow]: # -> list[dict[str, Decimal | float]]
    """
    Return last_n months totals (income / expense / net)
    for one specific user, based on Transaction.period_month.
    Works well with SQLite.
    """
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
        .filter(Transaction.user_id == user_id)   # ✅ only this user's transactions
        .group_by(month_key)
        .order_by(month_key.desc())
        .limit(last_n)
        .all()
    )

    rows = list(reversed(rows))

    data: list[dict[str, Decimal | float]] = []
    for r in rows:
        income = Decimal(str(r.income))
        expense = Decimal(str(r.expense))

        data.append(
            {
                "month": r.month,
                "income": income,
                "expense": expense,
                "net": income - expense,
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


def split_bucket_totals(transactions: Iterable["Transaction"]) -> dict[str, Decimal]:
    totals = {
        "needs": Decimal("0"),
        "wants": Decimal("0"),
        "savings": Decimal("0"),  # savings_spend (deposits/investing)
        "unknown": Decimal("0"),  # optional: categories not in mapping
    }

    for t in transactions:
        if t.txn_type != "expense":
            continue

        bucket = CATEGORY_BUCKETS.get(t.category, "wants")
        amount = t.amount_home or Decimal("0")

        if bucket == "needs":
            totals["needs"] += amount
        elif bucket == "wants":
            totals["wants"] += amount
        elif bucket == "savings":
            totals["savings"] += amount
        else:
            totals["unknown"] += amount  # useful while you’re still adding categories

    return totals