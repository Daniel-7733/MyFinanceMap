"""
                            *************************************

                                 useful functions that is not
                                 Belong to any other category

                            *************************************
"""
from secrets import token_hex
from datetime import date


def generate_random_string(length_string: int = 32) -> str:
    """
    This function will return random string"
    
    :param length_string: Length of string
    :type length_string: int
    :return: Random string
    """""
    return token_hex(length_string)


def month_start(d: date) -> date:
    """Generate current date
    ex:
    date_paid = 2025-12-02
    period_month = month_start(date(2025, 11, 15)) → becomes 2025-11-01
    """
    return date(d.year, d.month, 1)
