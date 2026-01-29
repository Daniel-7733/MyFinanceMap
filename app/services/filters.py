from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MonthSelection:
    month_key: str          # "YYYY-MM" or "all"
    label: str              # "All" or "January 2026"
    period_month: date | None  # date(YYYY,MM,1) or None


def select_month(month_str: str | None, today_key: str, month_options: dict[str, str]) -> MonthSelection:
    """
    Rules:
    - if None -> default to today_key
    - "all" -> no filter
    - "YYYY-MM" -> filter Transaction.period_month == date(YYYY,MM,1)
    - invalid -> fallback to all
    """
    if not month_str:
        month_str = today_key

    if month_str == "all":
        return MonthSelection(month_key="all", label="All", period_month=None)

    try:
        year_str, mon_str = month_str.split("-")
        period_month_obj = date(int(year_str), int(mon_str), 1)
        label = month_options.get(month_str, month_str)
        return MonthSelection(month_key=month_str, label=label, period_month=period_month_obj)
    except ValueError:
        return MonthSelection(month_key="all", label="All", period_month=None)
