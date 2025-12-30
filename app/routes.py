"""
                            *************************************

                                        routes only
                              connects user actions to services

                            *************************************
"""
from flask import Blueprint, render_template, request, redirect, url_for, Response, flash
from decimal import Decimal


main: Blueprint = Blueprint("main", __name__)


@main.route("/")
def home() -> str:
    """
    :return: home page
    """
    return render_template(
        "index.html",
        amount=f"You have 20.00 USD"
    )


@main.route("/transactions")
def add_transaction() -> str:
    """
    :return: Add Transaction page
    """
    return render_template("add_transaction.html")


@main.route("/transactions", methods=["GET", "POST"])
def add() -> Response | str:
    """Getting transaction page and adding it to the database"""
    if request.method == "POST":
        amount: Decimal | str = request.form["amount"]
        Decimal(amount)

        currency: str = request.form["currency_code"]
        type_: str = request.form["txn_type"]
        note: str = request.form["note"]
        date_paid: str = request.form["date_paid"]
        period_month: str = request.form["period_month"]

        home_currency: str | None = request.form["home_currency_code"]
        if home_currency == "":
            home_currency = None

        rate: Decimal | str | None = request.form["exchange_rate"]
        if rate == "":
            rate = None
        else:
            Decimal(rate)
        amount_home: Decimal | str | None = request.form["amount_home"]
        if amount_home == "":
            amount_home = None
        else:
            Decimal(amount_home)

        i_: dict[str, Decimal | str | None]  = { # This is just an example for debugging; This will save in Transaction
            "amount": amount,
            "currency": currency,
            "type_": type_,
            "note": note,
            "date_paid": date_paid,
            "period_month": period_month,
            "home_currency_code": home_currency,
            "rate": rate,
            "amount_home": amount_home
        }
        print(i_)
        return redirect(url_for("main.home"))
    return render_template("add_transaction.html")