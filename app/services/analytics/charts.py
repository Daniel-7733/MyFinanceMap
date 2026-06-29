from __future__ import annotations
from decimal import Decimal
from typing import Any, Iterable
from ...models import Transaction
from collections import defaultdict
from app.constants import MONEY_2DP




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


def monthly_income_expense_date_series(transactions: Iterable[Transaction]) -> dict[str, list]:
    """
    Returns chart-ready data aligned by month:
    {
      "labels": ["2026-01-01", "2026-02-02"],
      "income": [3000.00, 2500.00],
      "expense": [1200.00, 1800.00]
    }
    """
    income_by_month: dict[str, Decimal] = defaultdict(Decimal)
    expense_by_month: dict[str, Decimal] = defaultdict(Decimal)

    for t in transactions:
        month_key: str = t.date_paid.strftime("%Y-%m-%d")  # 2025-04-09
        if t.txn_type == "income":
            income_by_month[month_key] += (t.amount_home or Decimal("0"))
        elif t.txn_type == "expense":
            expense_by_month[month_key] += (t.amount_home or Decimal("0"))

    # union of months from both
    months: list[str] = sorted(set(income_by_month.keys()) | set(expense_by_month.keys()))

    labels: list[str] = months
    income_series: list[float] = [
        float(income_by_month[m].quantize(MONEY_2DP)) for m in months
    ]
    expense_series: list[float] = [
        float(expense_by_month[m].quantize(MONEY_2DP)) for m in months
    ]

    return {"labels": labels, "income": income_series, "expense": expense_series}


