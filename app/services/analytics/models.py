from typing import TypedDict
from decimal import Decimal

class MonthlyTotalRow(TypedDict): # This is far better than saying dict[str, Decimal | str]
    month: str
    income: Decimal
    expense: Decimal
    net: Decimal