from __future__ import annotations
from decimal import Decimal
from typing import Iterable
from sqlalchemy import func, case
from ...models import Transaction, db
from collections import defaultdict
from app.constants import MONEY_2DP


def top_expense_categories(transactions: Iterable["Transaction"], top_n: int = None) -> dict[str, Decimal]:
    """
    Returns chart-ready totals of expenses by category for the given transactions scope.
    :param transactions: transaction class (object)
    :param top_n: Number of transactions to return
    :return: a dictionary of names of category and their value
    """
    cat_dict: dict[str, Decimal] = {}
    for t in transactions:

        if t.txn_type != "expense":
            continue

        if t.category:
            if t.category not in cat_dict:
                cat_dict[t.category] = Decimal("0")

            cat_dict[t.category] += (t.amount_home or Decimal("0"))

    sorted_categories: list[tuple[str, Decimal]] = sorted(
        cat_dict.items(),
        key=lambda x: x[1],
        reverse=True
    )

    if top_n is None or top_n > len(sorted_categories):
        top_n = len(sorted_categories)

    sorted_categories = sorted_categories[:top_n]
    return dict(sorted_categories)


def income_by_category(transactions: Iterable["Transaction"], category_name: str) -> Decimal:
    """
    Calculates the total income for a specific category from an iterable of transactions.

    Example usage:
    salary_total = income_by_category(transactions, "salary")
    tips_total = income_by_category(transactions, "tips")

    :param transactions: An iterable collection of Transaction objects.
    :param category_name: The category to filter by (e.g., "salary", "tips").
    :return: The total accumulated amount as a Decimal.
    """
    total: Decimal = Decimal("0")

    for t in transactions:
        if t.txn_type != "income":
            continue

        if t.category != category_name:
            continue

        total += t.amount_home or Decimal("0")

    return total


def monthly_income_by_category(user_id: int, last_n: int = 6) -> list[dict[str, Decimal]]:
    """
    Fetches and aggregates monthly income by category for a specific user.

    Calculates the total salary, tips, and combined income for the last N months.
    Returns the data in chronological order.

    :param user_id: The ID of the user whose data is being queried.
    :param last_n: The number of recent months to include in the results.
    :return: A list of dictionaries containing monthly breakdown and totals.
    """

    month_key = func.strftime("%Y-%m", Transaction.period_month)

    salary_sum = func.coalesce(
        func.sum(
            case(
                (
                    (Transaction.txn_type == "income") &
                    (Transaction.category == "salary"),
                    Transaction.amount_home,
                ),
                else_=0,
            )
        ),
        0,
    )

    tips_sum = func.coalesce(
        func.sum(
            case(
                (
                    (Transaction.txn_type == "income") &
                    (Transaction.category == "tips"),
                    Transaction.amount_home,
                ),
                else_=0,
            )
        ),
        0,
    )

    rows = (
        db.session.query(
            month_key.label("month"),
            salary_sum.label("salary"),
            tips_sum.label("tips"),
        )
        .filter(Transaction.user_id == user_id)
        .group_by(month_key)
        .order_by(month_key.desc())
        .limit(last_n)
        .all()
    )

    rows = list(reversed(rows))

    data: list[dict[str, Decimal]] = []

    for r in rows:
        salary = Decimal(str(r.salary))
        tips = Decimal(str(r.tips))

        data.append({
            "month": r.month,
            "salary": salary,
            "tips": tips,
            "total": salary + tips,
        })

    return data


def category_expense_totals(transactions: Iterable["Transaction"]) -> dict[str, list]:
    """
    Returns chart-ready totals of expenses by category for the given transactions scope.
    (You should pass already-filtered transactions for a specific month.)

    Output:
    {
      "labels": ["rent", "groceries"],
      "totals": [500.00, 120.50]
    }
    """
    totals_by_category: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    for t in transactions:
        if t.txn_type != "expense":
            continue
        totals_by_category[t.category] += (t.amount_home or Decimal("0"))

    # Sort categories by total desc
    items = sorted(totals_by_category.items(), key=lambda x: x[1], reverse=True)

    labels: list[str] = [cat for cat, _ in items]
    totals: list[float] = [float(total.quantize(MONEY_2DP)) for _, total in items]

    return {"labels": labels, "totals": totals}

