from decimal import Decimal

from app.services.analytics.behavior import category_changes


def test_category_changes():
    previous = {
        "food": Decimal("800"),
        "transport": Decimal("300"),
    }

    current = {
        "food": Decimal("1000"),
        "transport": Decimal("240"),
    }

    result = category_changes(previous, current)

    assert result == [
        {
            "category": "food",
            "previous": Decimal("800"),
            "current": Decimal("1000"),
            "change_percentage": Decimal("25"),
        },
        {
            "category": "transport",
            "previous": Decimal("300"),
            "current": Decimal("240"),
            "change_percentage": Decimal("-20"),
        },
    ]


def test_category_changes_skips_category_without_history():
    previous = {
        "food": Decimal("800"),
    }

    current = {
        "food": Decimal("1000"),
        "gym": Decimal("200"),
    }

    result = category_changes(previous, current)

    assert result == [
        {
            "category": "food",
            "previous": Decimal("800"),
            "current": Decimal("1000"),
            "change_percentage": Decimal("25"),
        },
    ]

def test_category_changes_skips_zero_previous_amount():
    previous = {
        "food": Decimal("0"),
    }

    current = {
        "food": Decimal("500"),
    }

    result = category_changes(previous, current)

    assert result == []