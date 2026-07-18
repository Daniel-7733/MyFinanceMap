import pytest
from decimal import Decimal

from app.services.analytics.volatility import value_range, variance, standard_deviation


@pytest.mark.parametrize(
    "values, expected",
    [
        ([], Decimal("0")),
        ([Decimal("100")], Decimal("0")),
        ([Decimal("100"), Decimal("120"), Decimal("90")], Decimal("30")),
        ([Decimal("-50"), Decimal("50")], Decimal("100")),
        ([Decimal("5"), Decimal("5"), Decimal("5")], Decimal("0")),
    ],
)
def test_value_range(values, expected):
    assert value_range(values) == expected



@pytest.mark.parametrize(
    "values, expected",
    [
        (
            [],
            Decimal("0"),
        ),
        (
            [Decimal("100")],
            Decimal("0"),
        ),
        (
            [Decimal("5"), Decimal("5"), Decimal("5")],
            Decimal("0"),
        ),
        (
            [Decimal("100"), Decimal("120"), Decimal("140")],
            Decimal("266.6666666666666666666666667"),
        ),
    ],
)
def test_variance(values, expected):
    assert variance(values) == expected


@pytest.mark.parametrize(
    "variance_value, expected",
    [
        (Decimal("0"), Decimal("0")),
        (Decimal("1"), Decimal("1")),
        (Decimal("4"), Decimal("2")),
        (Decimal("9"), Decimal("3")),
        (Decimal("2.25"), Decimal("1.5")),
    ],
)
def test_standard_deviation(variance_value, expected):
    assert standard_deviation(variance_value) == expected