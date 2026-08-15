from typing import TypedDict
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum



# ================================== #
#              TypedDict
# ================================== #
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



# ================================== #
#               Enum
# ================================== #
class FinancialMetric(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    SAVING = "saving"
    DEBT = "debt"



# ============ @dataclass ============ #
@dataclass(frozen=True)
class Recommendation:
    message: str
    priority: str
    reason: str


@dataclass(frozen=True)
class BehaviorPattern:
    direction: str
    direction_consistency: Decimal
    magnitude_stability: Decimal
    pattern: str


@dataclass(frozen=True)
class ConfidenceResult:
    score: Decimal
    level: str


@dataclass(frozen=True)
class FinancialReport:
    analysis_months: int

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
    behavior: BehaviorPattern | None
    recommendation: Recommendation

