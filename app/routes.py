"""
                            *************************************

                                        routes only
                              connects user actions to services

                            *************************************
"""
from flask import Blueprint, render_template

main: Blueprint = Blueprint("main", __name__)


@main.route("/")
def home() -> str:
    return render_template(
        "index.html",
        amount=f"You have 20.00 USD"
    )

