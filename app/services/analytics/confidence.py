# ===================================
# Responsibilities → evaluates how trustworthy that prediction is
#
#                  The pipeline
# Volatility ───────────────┐
#                           │
# Number of months ─────────┼→ Confidence Score → Confidence Level
#                           │
# Trend consistency ────────┘
#
#            Clear Pipline of this page
#                 volatility.py
#                     ↓
#                 CV = 8%
#
#                 trends.py
#                     ↓
#                 Consistency = 90%
#
#                 monthly history
#                     ↓
#                 6 months
#
#                         ↓
#
#                 confidence.py
#
#                 Volatility → 85 points
#                 History    → 80 points
#                 Trend      → 90 points
#
#                         ↓
#
#                 confidence_score()
#
#                         ↓
#
#                 85 points
#
#                         ↓
#
#                 confidence_level()
#
#                         ↓
#
#                 "High"
#
#                         ↓
#
#                 ConfidenceResult(
#                     score=85,
#                     level="High"
#                 )
# ===================================

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ConfidenceResult:
    score: Decimal
    level: str


def volatility_confidence_score(cv: Decimal) -> Decimal:
    """
    Question:
    How much confidence should we give based on volatility?

    Lower volatility = higher confidence.
    """
    if cv < Decimal("5"):
        return Decimal("100")

    if cv < Decimal("10"):
        return Decimal("85")

    if cv < Decimal("20"):
        return Decimal("65")

    if cv < Decimal("40"):
        return Decimal("40")

    return Decimal("20")


def history_confidence_score(number_of_months: int) -> Decimal:
    """
    Question:
    How much confidence should we give based on
    the amount of historical evidence?
    """
    if number_of_months <= 0:
        return Decimal("0")

    if number_of_months == 1:
        return Decimal("20")

    if number_of_months == 2:
        return Decimal("40")

    if number_of_months < 6:
        return Decimal("60")

    if number_of_months < 12:
        return Decimal("80")

    return Decimal("100")


def trend_confidence_score(trend_consistency: Decimal) -> Decimal:
    """
    Question:
    How much confidence should we give based on
    trend consistency?

    trend_consistency is expected to be between 0 and 100.
    """
    if trend_consistency < Decimal("0"):
        return Decimal("0")

    if trend_consistency > Decimal("100"):
        return Decimal("100")

    return trend_consistency


def confidence_score(cv: Decimal, number_of_months: int, trend_consistency: Decimal) -> Decimal:
    """
    Combine the confidence contributions into
    one overall forecast-confidence score.
    """
    volatility_points = volatility_confidence_score(cv)
    history_points = history_confidence_score(number_of_months)
    trend_points = trend_confidence_score(trend_consistency)

    total = volatility_points + history_points + trend_points

    return total / Decimal("3")


def confidence_level(score: Decimal) -> str:
    if score >= Decimal("90"):
        return "Very High"

    if score >= Decimal("75"):
        return "High"

    if score >= Decimal("50"):
        return "Moderate"

    if score >= Decimal("25"):
        return "Low"

    return "Very Low"


def evaluate_confidence(cv: Decimal, number_of_months: int, trend_consistency: Decimal) -> ConfidenceResult:

    score = confidence_score(
        cv=cv,
        number_of_months=number_of_months,
        trend_consistency=trend_consistency,
    )

    level = confidence_level(score)

    return ConfidenceResult(
        score=score,
        level=level,
    )

