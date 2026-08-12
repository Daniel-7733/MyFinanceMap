from decimal import Decimal
from app.services.analytics.models import MonthlyTotalRow, ForecastResult


def forecast_next_month(month_data: list[MonthlyTotalRow]) -> ForecastResult:
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


