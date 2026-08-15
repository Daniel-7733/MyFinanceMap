# ===================================================================
# Responsibility is: Build a complete financial analysis report from specialist outputs.
# ===================================================================
import decimal
from decimal import Decimal

from .behavior import analyze_behavior_pattern
from .models import MonthlyTotalRow, FinancialReport, Recommendation, FinancialMetric, BehaviorPattern
from .confidence import ConfidenceResult, evaluate_confidence
from .forecast import forecast_next_month
from .preparation import completed_months
from .recommendation import recommend_from_behavior
from .trends import trend_direction, trend_consistency
from .volatility import coefficient_of_variation, volatility_level



def generate_financial_report(monthly_data: list[MonthlyTotalRow], number_of_months: int = 3) -> FinancialReport:

    """
        Pipline
                          monthly_data
                           ↓
                   completed_months()
                           ↓
                    select last N
                           ↓
               ┌───────────┼───────────┐
               ↓           ↓           ↓
             Trend     Volatility   Forecast
               │           │           │
               └───────────┼───────────┘
                           ↓
                       Confidence
                           ↓
                    FinancialReport

    :param monthly_data:
    :param number_of_months:
    :return:
    """

    completed_data = completed_months(monthly_data)
    selected_data = completed_data[-number_of_months:]

    income_values: list[Decimal] = [row["income"] for row in selected_data]
    expense_values: list[Decimal] = [row["expense"] for row in selected_data]
    net_values: list[Decimal] = [row["net"] for row in selected_data]

    income_total = sum(income_values, decimal.Decimal("0"))
    expense_total = sum(expense_values, decimal.Decimal("0"))
    net_total = income_total - expense_total

    direction = trend_direction(net_values)
    consistency = trend_consistency(net_values)

    cv = coefficient_of_variation(expense_values)
    volatility_name = volatility_level(cv)

    forecast = forecast_next_month(selected_data)

    confidence = evaluate_confidence(
        cv=cv,
        number_of_months=len(selected_data),
        trend_consistency=consistency,
    )

    behavior: BehaviorPattern | None = analyze_behavior_pattern(expense_values)

    recommendation = recommend_from_behavior(
        FinancialMetric.EXPENSE,
        behavior,
    )

    return FinancialReport(
        analysis_months=len(selected_data),

        income=income_total,
        expense=expense_total,
        net=net_total,

        trend_direction=direction,
        trend_consistency=consistency,

        volatility_score=cv,
        volatility_level=volatility_name,

        forecast_income=forecast["income"],
        forecast_expense=forecast["expense"],
        forecast_net=forecast["net"],

        confidence=confidence,
        behavior=behavior,
        recommendation=recommendation,
    )
