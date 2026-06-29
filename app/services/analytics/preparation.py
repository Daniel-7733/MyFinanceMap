from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import Any


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


