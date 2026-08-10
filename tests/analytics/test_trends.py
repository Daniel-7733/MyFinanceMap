import pytest
from decimal import Decimal
from app.services.analytics.trends import percentage_change, difference, trend_direction, trend_consistency


@pytest.mark.parametrize(
    "old_value, new_value, expected",
    [
        (Decimal("100"), Decimal("120"), Decimal("20")),     # 20% Increase
        (Decimal("100"), Decimal("80"), Decimal("-20")),     # 20% Decrease
        (Decimal("-100"), Decimal("-120"), Decimal("-20")),  # Negative baseline decrease
        (Decimal("-100"), Decimal("-80"), Decimal("20")),    # Negative baseline increase
        (Decimal("0"), Decimal("50"), Decimal("0")),         # Zero division safety
        (Decimal("50"), Decimal("50"), Decimal("0")),        # No change
    ]
)
def test_percentage_change(old_value, new_value, expected):
    assert percentage_change(old_value, new_value) == expected


@pytest.mark.parametrize(
    "first, second, expected",
    [
        (Decimal("100"), Decimal("150"), Decimal("50")),    # Positive difference
        (Decimal("150"), Decimal("100"), Decimal("-50")),   # Negative difference
        (Decimal("-50"), Decimal("50"), Decimal("100")),    # Crossing zero upward
        (Decimal("50"), Decimal("50"), Decimal("0")),       # Equal values
    ]
)
def test_difference(first, second, expected):
    assert difference(first, second) == expected


@pytest.mark.parametrize(
    "values, expected",
    [
        # Edge cases
        ([], "Not enough data"),
        ([Decimal("100")], "Not enough data"),

        # Strongly Improving (>= 20%)
        ([Decimal("100"), Decimal("120")], "Strongly Improving"),
        ([Decimal("100"), Decimal("150"), Decimal("130")], "Strongly Improving"),  # Middle values ignored

        # Slightly Improving (>= 5% and < 20%)
        ([Decimal("100"), Decimal("105")], "Slightly Improving"),
        ([Decimal("100"), Decimal("119.9")], "Slightly Improving"),

        # Stable (>-5% and < 5%)
        ([Decimal("100"), Decimal("104.9")], "Stable"),
        ([Decimal("100"), Decimal("95.1")], "Stable"),
        ([Decimal("100"), Decimal("100")], "Stable"),

        # Slightly Declining (<= -5% and > -20%)
        ([Decimal("100"), Decimal("95")], "Slightly Declining"),
        ([Decimal("100"), Decimal("80.1")], "Slightly Declining"),

        # Strongly Declining (<= -20%)
        ([Decimal("100"), Decimal("80")], "Strongly Declining"),
        ([Decimal("100"), Decimal("50")], "Strongly Declining"),

        # Zero baseline handling (returns 0% change -> Stable)
        ([Decimal("0"), Decimal("100")], "Stable"),
    ]
)
def test_trend_direction(values, expected):
    assert trend_direction(values) == expected


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
            [Decimal("100"), Decimal("110")],
            Decimal("100"),
        ),
        (
            [
                Decimal("100"),
                Decimal("110"),
                Decimal("120"),
                Decimal("130"),
            ],
            Decimal("100"),
        ),
        (
            [
                Decimal("100"),
                Decimal("90"),
                Decimal("80"),
                Decimal("70"),
            ],
            Decimal("100"),
        ),
        (
            [
                Decimal("100"),
                Decimal("110"),
                Decimal("105"),
                Decimal("120"),
            ],
            Decimal("66.66666666666666666666666667"),
        ),
        (
            [
                Decimal("100"),
                Decimal("100"),
                Decimal("100"),
                Decimal("100"),
            ],
            Decimal("100"),
        ),
    ],
)
def test_trend_consistency(values, expected):
    assert trend_consistency(values) == expected

