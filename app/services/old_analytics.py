"""
                            *************************************

                            The brain of the app: analytics logic
                                 summaries, totals, trends

                            *************************************
"""
from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterable
from sqlalchemy import func, case
from ..models import Transaction, db
from collections import defaultdict
from app.constants import MONEY_2DP, CATEGORY_BUCKETS



def monthly_totals(user_id: int, last_n: int = 6) -> list[dict[str, Decimal | float]]:
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


def prepare_top_categories(top_expense_cat: dict[str, Decimal], expense_total: Decimal) -> list[dict[str, Decimal]]:
    """
    Calculates the percentage of total expenses for each top expense category.

    :param top_expense_cat: A dictionary mapping category names to their respective expense amounts.
    :param expense_total: The absolute total expense amount used to calculate percentages.
    :return: A list of dictionaries, where each dictionary contains the category name,
    the raw amount, and its calculated percentage relative to the total.
    """
    top_categories: list[dict[str, Decimal]] = []

    for category, amount in top_expense_cat.items():
        percentage = Decimal("0")

        if expense_total > 0:
            percentage: Decimal = (amount / expense_total) * Decimal("100")

        top_categories.append({
            "category": category,
            "amount": amount,
            "percentage": percentage,
        })
    return top_categories


def prepare_monthly_trend(month_data: list[dict[str, Any]]) -> list[dict[str, Decimal]]:
    """
    Formats raw monthly data into human-readable trend metrics.

    :param month_data: A list of dictionaries containing raw keys "month" (YYYY-MM), "income", and "net".
    :return: A list of dictionaries containing formatted month names, net amounts, and the net savings rate percentage relative to income.
    """
    monthly_trend: list[dict[str, Decimal]] = []

    for row in month_data:

        month_name: str = datetime.strptime(
            row["month"],
            "%Y-%m"
        ).strftime("%B %Y")

        percentage: Decimal = Decimal("0")

        income: Decimal = Decimal(str(row["income"]))
        net: Decimal = Decimal(str(row["net"]))

        if income > 0:
            percentage = (net / income) * Decimal("100")

        monthly_trend.append({
            "month": month_name,
            "net": net,
            "percentage": percentage,
        })

    return monthly_trend


def forecast_next_month(month_data: list[dict[str, Decimal | float]]) -> dict[str, Decimal]:
    """
    Predicts the next month's finances using a simple average of historical data.

    :param month_data: A list of dictionaries containing "income" and "expense" keys.
    :return: A dictionary containing the forecasted "income", "expense", and "net" savings
        for the upcoming month. Returns zeroes if input data is empty.
    """
    if not month_data:
        return {
            "income": Decimal("0"),
            "expense": Decimal("0"),
            "net": Decimal("0"),
        }

    income_total: Decimal | float = sum(row["income"] for row in month_data)
    expense_total: Decimal | float = sum(row["expense"] for row in month_data)

    count: Decimal = Decimal(str(len(month_data)))

    predicted_income: Decimal = Decimal(income_total) / count
    predicted_expense: Decimal = Decimal(expense_total) / count

    return {
        "income": predicted_income,
        "expense": predicted_expense,
        "net": predicted_income - predicted_expense,
    }


def completed_months(month_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Remove the current incomplete month from monthly totals. Ex: current month is June.
    This function will ignore the current month and finsh the list of months by previous month (May)
    """
    current_month: str = date.today().strftime("%Y-%m")

    return [
        row for row in month_data
        if row["month"] < current_month
    ]


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


def statistics(amounts: list[Decimal]) -> dict[str, Decimal]:
    """
    Function to calculate the expense statistics. Note: if the amount is empty, the function return 0 for all
    maximum, minimum, and average.
    :param amounts: (Decimal) a list of amount.
    :return: maximum, minimum, and average amount.
    """
    zero = Decimal("0")

    if not amounts:
        return {
            "min": zero,
            "max": zero,
            "average": zero,
        }

    total_expense: Decimal = sum(amounts)
    count: Decimal = Decimal(len(amounts))

    return {
        "min": min(amounts),
        "max": max(amounts),
        "average": total_expense / count,
    }

