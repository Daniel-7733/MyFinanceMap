from decimal import Decimal

from app.services.analytics.report import FinancialReport, generate_financial_report


def test_generate_financial_report():
    month_data = [
        {
            "month": "2026-05",
            "income": Decimal("3000"),
            "expense": Decimal("2000"),
            "net": Decimal("1000"),
        },
        {
            "month": "2026-06",
            "income": Decimal("3000"),
            "expense": Decimal("2100"),
            "net": Decimal("900"),
        },
        {
            "month": "2026-07",
            "income": Decimal("3000"),
            "expense": Decimal("2200"),
            "net": Decimal("800"),
        },
        {
            "month": "2026-08",
            "income": Decimal("0"),
            "expense": Decimal("50000"),
            "net": Decimal("-50000"),
        }
    ]

    report = generate_financial_report(
        monthly_data=month_data,
        number_of_months=3,
    )

    assert isinstance(report, FinancialReport)

    assert report.income == Decimal("9000")
    assert report.expense == Decimal("6300")
    assert report.net == Decimal("2700")

    assert report.forecast_income == Decimal("3000")
    assert report.forecast_expense == Decimal("2100")
    assert report.forecast_net == Decimal("900")