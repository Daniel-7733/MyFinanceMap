# ===================================
# recommendation.py → decides what advice follows from that description
# ===================================
from app.constants.behavior import BEHAVIOR_DIRECTION_CONSISTENCY_THRESHOLD, BEHAVIOR_MAGNITUDE_STABILITY_THRESHOLD
from app.services.analytics.models import Recommendation, BehaviorPattern, FinancialMetric




# =========================================
#           Pipline
# =========================================

# BehaviorPattern
#     ↓
# FinancialMetric
#     ↓
# direction_impact()
#     ↓
# pattern consistency / stability
#     ↓
# recommend_from_behavior()
#     ↓
# Recommendation

# =========================================

def direction_impact(metric: FinancialMetric, direction: str) -> int:
    """
    Translate a financial metric's direction into meaning.

    Returns:
         1 -> favorable
         0 -> neutral / unknown
        -1 -> unfavorable
    """

    if direction in ("Stable", "Not enough data"):
        return 0

    if metric in (
        FinancialMetric.INCOME,
        FinancialMetric.SAVING,
    ):
        if direction == "Increasing":
            return 1
        if direction == "Decreasing":
            return -1

    if metric in (
        FinancialMetric.EXPENSE,
        FinancialMetric.DEBT,
    ):
        if direction == "Increasing":
            return -1
        if direction == "Decreasing":
            return 1

    return 0

def recommend_from_behavior(metric: FinancialMetric, pattern: BehaviorPattern) -> Recommendation:
    """
    Create a recommendation from an observed financial behavior.

    Behavior describes what happened.
    Recommendation interprets what that behavior means.
    """

    impact: int = direction_impact(
        metric=metric,
        direction=pattern.direction,
    )

    if pattern.direction == "Not enough data":
        return Recommendation(
            message="Collect more historical data before making a recommendation.",
            priority="Low",
            reason="There is not enough data to identify a reliable behavior pattern.",
        )

    if impact == 0:
        return Recommendation(
            message=f"Continue monitoring your {metric.value}.",
            priority="Low",
            reason="No meaningful positive or negative direction was detected.",
        )

    if impact < 0:
        if (
            pattern.direction_consistency >= BEHAVIOR_DIRECTION_CONSISTENCY_THRESHOLD
            and pattern.magnitude_stability >= BEHAVIOR_MAGNITUDE_STABILITY_THRESHOLD
        ):
            return Recommendation(
                message=f"Review your {metric.value} because the unfavorable pattern is persistent.",
                priority="High",
                reason=(
                    f"{metric.value.capitalize()} is "
                    f"{pattern.direction.lower()} consistently."
                ),
            )

        return Recommendation(
            message=f"Monitor your {metric.value} closely and identify what is causing the irregular changes.",
            priority="Moderate",
            reason=(
                f"{metric.value.capitalize()} is moving in an unfavorable "
                "direction, but the behavior is inconsistent."
            ),
        )

    if (
        pattern.direction_consistency >= BEHAVIOR_DIRECTION_CONSISTENCY_THRESHOLD
        and pattern.magnitude_stability >= BEHAVIOR_MAGNITUDE_STABILITY_THRESHOLD
    ):
        return Recommendation(
            message=f"Maintain the current {metric.value} pattern.",
            priority="Low",
            reason=(
                f"{metric.value.capitalize()} is moving in a favorable "
                "and consistent direction."
            ),
        )

    return Recommendation(
        message=f"Your {metric.value} is moving favorably, but continue monitoring its stability.",
        priority="Low",
        reason=(
            f"{metric.value.capitalize()} is improving, "
            "but the pattern is irregular."
        ),
    )
