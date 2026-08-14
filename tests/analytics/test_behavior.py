from decimal import Decimal

from app.services.analytics.behavior import category_changes, consecutive_changes, magnitude_stability, \
    analyze_behavior_pattern


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

def test_consecutive_changes():
    values = [
        Decimal("700"),
        Decimal("760"),
        Decimal("720"),
        Decimal("850"),
    ]

    assert consecutive_changes(values) == [
        Decimal("60"),
        Decimal("-40"),
        Decimal("130"),
    ]

def test_magnitude_stability_perfectly_stable():
    values = [
        Decimal("700"),
        Decimal("750"),
        Decimal("800"),
        Decimal("850"),
    ]

    assert magnitude_stability(values) == Decimal("1")

def test_magnitude_stability_not_enough_data():
    assert magnitude_stability([]) is None

    assert magnitude_stability(
        [Decimal("100")]
    ) is None

    assert magnitude_stability(
        [
            Decimal("100"),
            Decimal("120"),
        ]
    ) is None

def test_analyze_behavior_pattern_increasing_and_inconsistent():
    values = [
        Decimal("700"),
        Decimal("760"),
        Decimal("720"),
        Decimal("850"),
    ]

    result = analyze_behavior_pattern(values)

    assert result is not None

    assert result.direction == "Increasing"

    assert result.direction_consistency == (
        Decimal("2")
        / Decimal("3")
        * Decimal("100")
    )

    assert result.pattern == "Increasing and highly inconsistent"

def test_analyze_behavior_pattern_consistently_increasing():
    values = [
        Decimal("700"),
        Decimal("750"),
        Decimal("800"),
        Decimal("850"),
    ]

    result = analyze_behavior_pattern(values)

    assert result is not None

    assert result.direction == "Increasing"
    assert result.direction_consistency == Decimal("100")
    assert result.magnitude_stability == Decimal("1")
    assert result.pattern == "Consistently increasing"

