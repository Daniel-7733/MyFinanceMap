from decimal import Decimal
from app.services.analytics.forecast import forecast_next_month


def test_forecast_next_month() -> None:
    month_data: list[dict[str, str | Decimal]] = [
        {
            "month": "2026-03",
            "income": Decimal("3000"),
            "expense": Decimal("2000"),
            "net": Decimal("1000"),
        },
        {
            "month": "2026-04",
            "income": Decimal("3000"),
            "expense": Decimal("1800"),
            "net": Decimal("1200"),
        },
        {
            "month": "2026-05",
            "income": Decimal("3000"),
            "expense": Decimal("2200"),
            "net": Decimal("800"),
        },
    ]

    forecast: dict[str, Decimal] = forecast_next_month(month_data)

    assert forecast["income"] == Decimal("3000")
    assert forecast["expense"] == Decimal("2000")
    assert forecast["net"] == Decimal("1000")

