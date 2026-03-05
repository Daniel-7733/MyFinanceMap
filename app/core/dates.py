from datetime import date, datetime
from zoneinfo import ZoneInfo


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


def get_full_current_date() -> str:
    """
    :return: MM-DD, YYYY HH:MM:SS (December 27, 2022 10:09:20)
    """

    now: datetime = datetime.now()
    return now.strftime("%B %d, %Y %H:%M:%S")

def get_local_time(user_timezone: str) -> str:
    now = datetime.now(ZoneInfo(user_timezone))
    return now.strftime("%A, %B %d, %Y %H:%M")