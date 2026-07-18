"""
Volatility
↓
"How stable is that direction?"
"""
from decimal import Decimal

def value_range(values: list[Decimal]) -> Decimal:
    """Return the difference between the largest and smallest values.

    Examples:
        [1000, 1100, 1200] → 200
        [1000, 2500, 400]  → 2100
    """
    if not values:
        return Decimal("0")
    return max(values) - min(values)

def average(values: list[Decimal]) -> Decimal:
    if not values:
        return Decimal("0")

    count: Decimal = Decimal(len(values))
    return sum(values) / count

def deviations(values: list[Decimal], mean: Decimal) -> list[Decimal]:
    """Return each value's distance from the mean.

    Example:
        Mean = 120

        100 - 120 = -20
        120 - 120 =   0
        140 - 120 =  20
    """
    return [value - mean for value in values]

def square(values: list[Decimal]) -> list[Decimal]:
    """Return the square of each value.

    Example:
        (-20)^2 = 400
        0^2     = 0
        20^2    = 400
    """
    return [value ** 2 for value in values]

def variance(values: list[Decimal]) -> Decimal:
    """
    values
      ↓
    calculate mean
      ↓
    calculate each deviation
      ↓
    square each deviation
      ↓
    add squared deviations
      ↓
    divide by count
      ↓
    variance

    example: variance = (400 + 0 + 400) / 3
         = 266.666...
    Return the population variance.
    """
    if not values:
        return Decimal("0")
    mean: Decimal = average(values)
    deviation: list[Decimal] = deviations(values, mean)
    squares: list[Decimal] = square(deviation)
    return average(squares)

def standard_deviation(variance_value: Decimal) -> Decimal:
    """Return the square root of the population variance."""
    if variance_value <= 0:
        return Decimal("0")
    return variance_value.sqrt()

