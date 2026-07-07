import pytest
from decimal import Decimal
from app.services.analytics.statistics import statistics

@pytest.mark.parametrize(
    "amounts, expected",
    [
        # 1. Empty list case
        (
                [],
                {"min": Decimal("0"), "max": Decimal("0"), "average": Decimal("0")}
        ),
        # 2. Single element case
        (
                [Decimal("10.50")],
                {"min": Decimal("10.50"), "max": Decimal("10.50"), "average": Decimal("10.50")}
        ),
        # 3. Standard positive values
        (
                [Decimal("10.00"), Decimal("20.00"), Decimal("30.00")],
                {"min": Decimal("10.00"), "max": Decimal("30.00"), "average": Decimal("20.00")}
        ),
        # 4. Floating decimals
        (
                [Decimal("1.25"), Decimal("2.50"), Decimal("3.75"), Decimal("5.00")],
                {"min": Decimal("1.25"), "max": Decimal("5.00"), "average": Decimal("3.125")}
        ),
        # 5. Negative and zero values (e.g., refunds)
        (
                [Decimal("-50.00"), Decimal("0.00"), Decimal("100.00")],
                {"min": Decimal("-50.00"), "max": Decimal("100.00"),
                 "average": Decimal("16.66666666666666666666666667")}
        ),
        # 6. Identical values
        (
                [Decimal("5.55"), Decimal("5.55"), Decimal("5.55")],
                {"min": Decimal("5.55"), "max": Decimal("5.55"), "average": Decimal("5.55")}
        ),
    ]
)
def test_statistics(amounts, expected):
    assert statistics(amounts) == expected
