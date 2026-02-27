"""
                            user settings (currency, timezone, categories)

                            Make another blueprint for auth:
                            -> auth blueprint (login/register/logout)
                            (Like "main blueprint (transactions + dashboard)" in rout.py)

"""

from flask import Blueprint

auth: Blueprint = Blueprint("auth", __name__)

