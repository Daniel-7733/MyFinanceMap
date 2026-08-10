# =======================================
# Small pieces
# ├── volatility_confidence_score()
# ├── history_confidence_score()
# ├── trend_confidence_score()
# ├── confidence_score()
# └── confidence_level()
#
#             ↓
#
# Whole module
# └── evaluate_confidence()
# =======================================

import pytest
from decimal import Decimal

from app.services.analytics.confidence import (
    ConfidenceResult,
    volatility_confidence_score,
    history_confidence_score,
    trend_confidence_score,
    confidence_score,
    confidence_level,
    evaluate_confidence,
)


@pytest.mark.parametrize(
    "cv, expected",
    [
        (Decimal("0"), Decimal("100")),
        (Decimal("4.99"), Decimal("100")),
        (Decimal("5"), Decimal("85")),
        (Decimal("9.99"), Decimal("85")),
        (Decimal("10"), Decimal("65")),
        (Decimal("19.99"), Decimal("65")),
        (Decimal("20"), Decimal("40")),
        (Decimal("39.99"), Decimal("40")),
        (Decimal("40"), Decimal("20")),
        (Decimal("100"), Decimal("20")),
    ],
)
def test_volatility_confidence_score(cv, expected):
    assert volatility_confidence_score(cv) == expected


@pytest.mark.parametrize(
    "months, expected",
    [
        (0, Decimal("0")),
        (1, Decimal("20")),
        (2, Decimal("40")),
        (3, Decimal("60")),
        (5, Decimal("60")),
        (6, Decimal("80")),
        (11, Decimal("80")),
        (12, Decimal("100")),
        (24, Decimal("100")),
    ],
)
def test_history_confidence_score(months, expected):
    assert history_confidence_score(months) == expected


@pytest.mark.parametrize(
    "consistency, expected",
    [
        (Decimal("-10"), Decimal("0")),
        (Decimal("0"), Decimal("0")),
        (Decimal("35"), Decimal("35")),
        (Decimal("66.67"), Decimal("66.67")),
        (Decimal("100"), Decimal("100")),
        (Decimal("150"), Decimal("100")),
    ],
)
def test_trend_confidence_score(consistency, expected):
    assert trend_confidence_score(consistency) == expected

def test_confidence_score():
    result = confidence_score(
        cv=Decimal("8"),
        number_of_months=6,
        trend_consistency=Decimal("90"),
    )

    # volatility = 85
    # history    = 80
    # trend      = 90
    #
    # (85 + 80 + 90) / 3 = 85

    assert result == Decimal("85")

@pytest.mark.parametrize(
    "score, expected",
    [
        (Decimal("100"), "Very High"),
        (Decimal("90"), "Very High"),
        (Decimal("89.99"), "High"),
        (Decimal("75"), "High"),
        (Decimal("74.99"), "Moderate"),
        (Decimal("50"), "Moderate"),
        (Decimal("49.99"), "Low"),
        (Decimal("25"), "Low"),
        (Decimal("24.99"), "Very Low"),
        (Decimal("0"), "Very Low"),
    ],
)
def test_confidence_level(score, expected):
    assert confidence_level(score) == expected

def test_evaluate_confidence():
    result = evaluate_confidence(
        cv=Decimal("8"),
        number_of_months=6,
        trend_consistency=Decimal("90"),
    )

    expected = ConfidenceResult(
        score=Decimal("85"),
        level="High",
    )

    assert result == expected
