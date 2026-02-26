from datetime import date


def month_start(d: date) -> date:
    """
    Return the first day of the month for date d.
    Example: 2025-11-15 -> 2025-11-01
    """
    return date(d.year, d.month, 1)


def get_current_month() -> tuple[str, str]:
    """
    Returns:
      - key:   "YYYY-MM"  (for <option value=""> and filtering)
      - label: "Month YYYY" (for showing to the user)
    """
    today: date = date.today()
    key: str = today.strftime("%Y-%m")      # "2026-01"
    label: str = today.strftime("%B %Y")    # "January 2026"
    return key, label