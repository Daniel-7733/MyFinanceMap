from decimal import Decimal
from app.services.analytics.models import CategoryChange

# ============================================
#
#                Pipline
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
def category_changes(previous: dict[str, Decimal],current: dict[str, Decimal],) -> list[CategoryChange]:
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
