import pytest
from decimal import Decimal

from app.services.analytics.models import (
    BehaviorPattern,
    FinancialMetric,
    Recommendation,
)

from app.services.analytics.recommendation import (
    direction_impact,
    recommend_from_behavior,
)


@pytest.mark.parametrize(
    "metric, direction, expected",
    [
        (
            FinancialMetric.EXPENSE,
            "Increasing",
            -1,
        ),
        (
            FinancialMetric.EXPENSE,
            "Decreasing",
            1,
        ),
        (
            FinancialMetric.SAVING,
            "Increasing",
            1,
        ),
        (
            FinancialMetric.SAVING,
            "Decreasing",
            -1,
        ),
        (
            FinancialMetric.INCOME,
            "Increasing",
            1,
        ),
        (
            FinancialMetric.INCOME,
            "Decreasing",
            -1,
        ),
        (
            FinancialMetric.DEBT,
            "Increasing",
            -1,
        ),
        (
            FinancialMetric.DEBT,
            "Decreasing",
            1,
        ),
        (
            FinancialMetric.EXPENSE,
            "Stable",
            0,
        ),
        (
            FinancialMetric.EXPENSE,
            "Not enough data",
            0,
        ),
    ],
)
def test_direction_impact(
    metric,
    direction,
    expected,
):
    assert direction_impact(metric, direction) == expected

def test_recommend_from_behavior_persistent_unfavorable_expense():
    pattern = BehaviorPattern(
        direction="Increasing",
        direction_consistency=Decimal("90"),
        magnitude_stability=Decimal("0.85"),
        pattern="Consistently increasing",
    )

    result = recommend_from_behavior(
        FinancialMetric.EXPENSE,
        pattern,
    )

    expected = Recommendation(
        message=(
            "Review your expense because the unfavorable "
            "pattern is persistent."
        ),
        priority="High",
        reason="Expense is increasing consistently.",
    )

    assert result == expected

def test_recommend_from_behavior_irregular_unfavorable_expense():
    pattern = BehaviorPattern(
        direction="Increasing",
        direction_consistency=Decimal("60"),
        magnitude_stability=Decimal("0.40"),
        pattern="Increasing and highly inconsistent",
    )

    result = recommend_from_behavior(
        FinancialMetric.EXPENSE,
        pattern,
    )

    expected = Recommendation(
        message=(
            "Monitor your expense closely and identify "
            "what is causing the irregular changes."
        ),
        priority="Moderate",
        reason=(
            "Expense is moving in an unfavorable direction, "
            "but the behavior is inconsistent."
        ),
    )

    assert result == expected

def test_recommend_from_behavior_favorable_saving():
    pattern = BehaviorPattern(
        direction="Increasing",
        direction_consistency=Decimal("100"),
        magnitude_stability=Decimal("0.90"),
        pattern="Consistently increasing",
    )

    result = recommend_from_behavior(
        FinancialMetric.SAVING,
        pattern,
    )

    assert result.priority == "Low"
    assert "favorable" in result.reason.lower()

def test_recommend_from_behavior_not_enough_data():
    pattern = BehaviorPattern(
        direction="Not enough data",
        direction_consistency=Decimal("0"),
        magnitude_stability=Decimal("0"),
        pattern="Not enough data",
    )

    result = recommend_from_behavior(
        FinancialMetric.EXPENSE,
        pattern,
    )

    assert result.priority == "Low"
    assert "not enough data" in result.reason.lower()

