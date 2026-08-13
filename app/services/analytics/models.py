from typing import TypedDict
from decimal import Decimal
from dataclasses import dataclass

class MonthlyTotalRow(TypedDict): # This methode is far better than saying dict[str, Decimal | str]
    month: str
    income: Decimal
    expense: Decimal
    net: Decimal


class ForecastResult(TypedDict):
    income: Decimal
    expense: Decimal
    net: Decimal


class MonthlyTrend(TypedDict):
    month: str
    net: Decimal
    percentage: Decimal


class CategoryChange(TypedDict):
    category: str
    previous: Decimal
    current: Decimal
    change_percentage: Decimal


@dataclass(frozen=True)
class ConfidenceResult:
    score: Decimal
    level: str


@dataclass(frozen=True)
class FinancialReport:
    income: Decimal
    expense: Decimal
    net: Decimal

    trend_direction: str
    trend_consistency: Decimal

    volatility_score: Decimal
    volatility_level: str

    forecast_income: Decimal
    forecast_expense: Decimal
    forecast_net: Decimal

    confidence: ConfidenceResult

