import pytest
from decimal import Decimal
from app.services.analytics.forecast import forecast_next_month
from app.services.analytics.models import ForecastResult


@pytest.mark.parametrize(
    "month_data, expected_forecast",
    [
        # Scenario 1: Stable standard growth/spending
        (
                [
                    {"month": "2026-03", "income": Decimal("3000"), "expense": Decimal("2000"), "net": Decimal("1000")},
                    {"month": "2026-04", "income": Decimal("3000"), "expense": Decimal("1800"), "net": Decimal("1200")},
                    {"month": "2026-05", "income": Decimal("3000"), "expense": Decimal("2200"), "net": Decimal("800")},
                ],
                {"income": Decimal("3000"), "expense": Decimal("2000"), "net": Decimal("1000")}
        ),

        # Scenario 2: High expense month (Holiday/Emergency)
        (
                [
                    {"month": "2026-06", "income": Decimal("4000"), "expense": Decimal("2000"), "net": Decimal("2000")},
                    {"month": "2026-07", "income": Decimal("4000"), "expense": Decimal("3500"), "net": Decimal("500")},
                ],
                {"income": Decimal("4000"), "expense": Decimal("2750"), "net": Decimal("1250")}
        ),

        # Scenario 3: Zero activity month
        (
                [
                    {"month": "2026-08", "income": Decimal("0"), "expense": Decimal("0"), "net": Decimal("0")},
                ],
                {"income": Decimal("0"), "expense": Decimal("0"), "net": Decimal("0")}
        ),
    ]
)
def test_forecast_next_month(month_data, expected_forecast) -> None:
    # 1. Execute the function with the current scenario's dataset
    forecast: ForecastResult = forecast_next_month(month_data)

    # 2. Assert the whole dictionary matches the expected output directly
    assert forecast == expected_forecast

