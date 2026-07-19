# ===================================
# Responsibilities → thresholds and fixed policy values
# ===================================

from decimal import Decimal

VOLATILITY_STABLE_THRESHOLD = Decimal("5")
VOLATILITY_MODERATE_THRESHOLD = Decimal("10")
VOLATILITY_HIGH_THRESHOLD = Decimal("20")
VOLATILITY_VERY_HIGH_THRESHOLD = Decimal("40")