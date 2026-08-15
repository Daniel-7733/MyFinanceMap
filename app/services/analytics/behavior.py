# ===================================
# behavior.py → describes reality
# ===================================

from decimal import Decimal
from app.services.analytics.models import CategoryChange, BehaviorPattern
from app.services.analytics.trends import trend_consistency
from app.services.analytics.volatility import coefficient_of_variation


# ==============================================
#                   Pipline
# ==============================================
#
# Previous month categories
#           │
#           ├──────────────┐
#           │              │
#           ▼              ▼
# Current month        Previous month
#           │              │
#           └──────┬───────┘
#                  ▼
#         category_changes()
#                  ▼
#          Behavior signals
#
# ============================================
def category_changes(previous: dict[str, Decimal],current: dict[str, Decimal]) -> list[CategoryChange]:
    """
    Compare expense categories between two periods.

    Policy:
        A category must have historical data before its
        percentage change can be evaluated.

        Categories without comparable history are skipped.

    :param previous: Category totals from the previous period.
    :param current: Category totals from the current period.
    :return: Comparable category changes.
    """
    changes: list[CategoryChange] = []

    for category, current_amount in current.items():

        if category not in previous:
            continue

        previous_amount: Decimal = previous[category]

        if previous_amount == Decimal("0"):
            continue

        change_percentage: Decimal = (
            (current_amount - previous_amount)
            / previous_amount
        ) * Decimal("100")

        changes.append({
            "category": category,
            "previous": previous_amount,
            "current": current_amount,
            "change_percentage": change_percentage,
        })

    return changes

# ==============================================
#                   Pipline 2
# ==============================================

#                 Monthly values
#                       ↓
#                  Differences
#                       ↓
#            ┌──────────┴───────────┐
#            ▼                      ▼
#        Signs                   |Steps|
#    +, -, +                 60, 40, 130
#            │                      │
#            ▼                      ▼
# Direction consistency      Magnitude volatility
#            │                      │
#            └──────────┬───────────┘
#                       ▼
#                 Behavior pattern
#
# Direction score:
# -1 ───────── 0 ───────── +1
# downward    stable       upward
#
#
# Magnitude stability:
# 0 ─────────────────────── 1
# unstable                 stable

# =======================================================

def consecutive_changes(values: list[Decimal]) -> list[Decimal]:
    """
    Return the change between every two consecutive values.

    Example:
        [700, 760, 720, 850]
        ->
        [60, -40, 130]
    """
    if len(values) < 2:
        return []

    return [current - previous for previous, current in zip(values, values[1:])]

def magnitude_stability(values: list[Decimal]) -> Decimal | None:
    """
    Measure how consistent the sizes of consecutive changes are.

    Returns:
        1 -> very stable movement sizes
        0 -> highly unstable movement sizes
        None -> not enough data to evaluate a pattern
    """
    if len(values) < 3:
        return None

    changes: list[Decimal] = consecutive_changes(values)
    magnitudes: list[Decimal] = [abs(change) for change in changes]
    cv: Decimal = coefficient_of_variation(magnitudes)
    cv_ratio: Decimal = cv / Decimal("100")

    if cv_ratio > Decimal("1"):
        cv_ratio = Decimal("1")

    return Decimal("1") - cv_ratio


def behavior_direction(values: list[Decimal]) -> str:
    """
    Return a neutral direction for behavior analysis.

    Increasing, Decreasing, Stable, or Not enough data.
    """
    if len(values) < 2:
        return "Not enough data"

    if values[-1] > values[0]:
        return "Increasing"

    if values[-1] < values[0]:
        return "Decreasing"

    return "Stable"

def classify_behavior_pattern(direction: str, direction_consistency: Decimal,
                              magnitude_stability_score: Decimal) -> str:
    """
    Translate behavioral measurements into human-readable meaning.
    """
    direction_is_consistent: bool = (
        direction_consistency >= Decimal("75")
    )

    magnitude_is_stable: bool = (
        magnitude_stability_score >= Decimal("0.70")
    )

    if direction == "Stable" and magnitude_is_stable:
        return "Stable behavior"

    if direction_is_consistent and magnitude_is_stable:
        return f"Consistently {direction.lower()}"

    if direction_is_consistent and not magnitude_is_stable:
        return f"{direction} with irregular magnitude"

    if not direction_is_consistent and magnitude_is_stable:
        return f"{direction} but direction is inconsistent"

    return f"{direction} and highly inconsistent"

def analyze_behavior_pattern(values: list[Decimal]) -> BehaviorPattern | None:
    """
    Analyze repeated behavior across at least three observations.
    """
    if len(values) < 3:
        return None

    direction = behavior_direction(values)
    consistency = trend_consistency(values)
    stability = magnitude_stability(values)

    if stability is None:
        return None

    pattern = classify_behavior_pattern(
        direction=direction,
        direction_consistency=consistency,
        magnitude_stability_score=stability,
    )

    return BehaviorPattern(
        direction=direction,
        direction_consistency=consistency,
        magnitude_stability=stability,
        pattern=pattern,
    )
