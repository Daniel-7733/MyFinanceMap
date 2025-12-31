"""
                            *************************************

                                        routes only
                              connects user actions to services

                            *************************************
"""
from flask import Blueprint, render_template, request, redirect, url_for, Response, flash
from decimal import Decimal, InvalidOperation
from datetime import date


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


@main.route("/transactions", methods=["GET", "POST"])
def add_transaction() -> Response | str:
    """
    Getting transaction page and adding it to the database and open the transaction page
    :return: Add Transaction page
     """
    if request.method == "POST":
        amount_raw: str = request.form.get("amount", "").strip() # Safer than request.form["x"] (doesn't crash if missing)
        try:
            amount: Decimal = Decimal(amount_raw)
        except (InvalidOperation, TypeError):
            flash("Amount must be a valid number like 19.00", "error")
            return render_template("add_transaction.html")

        currency: str = request.form.get("currency_code", "").strip().upper()
        txn_type: str = request.form.get("txn_type", "").strip()
        category: str = request.form.get("category", "").strip()
        note: str = request.form.get("note", "").strip()

        date_paid_raw: str = request.form.get("date_paid", "").strip()
        period_month_raw: str = request.form.get("period_month", "").strip()

        # Convert dates
        try:
            date_paid_obj: date = date.fromisoformat(date_paid_raw) if date_paid_raw else date.today()
        except ValueError:
            flash("Date Paid must be a valid date.", "error")
            return render_template("add_transaction.html")

        try:
            year_str, month_str = period_month_raw.split("-")
            period_month_obj: date = date(int(year_str), int(month_str), 1)
        except Exception:
            flash("Period Month must be a valid month.", "error")
            return render_template("add_transaction.html")

        home_currency: str | None = request.form.get("home_currency_code", "").strip().upper() or None

        rate_raw: str = request.form.get("exchange_rate", "").strip()
        rate: Decimal | None = None
        if rate_raw:
            try:
                rate = Decimal(rate_raw)
            except (InvalidOperation, TypeError):
                flash("Exchange rate must be a valid number like 1.25", "error")
                return render_template("add_transaction.html")

        amount_home_raw: str = request.form.get("amount_home", "").strip()
        amount_home: Decimal | None = None
        if amount_home_raw:
            try:
                amount_home = Decimal(amount_home_raw)
            except (InvalidOperation, TypeError):
                flash("Home amount must be a valid number like 25.00", "error")
                return render_template("add_transaction.html")

        # Multi-currency validation
        multi_used: bool = any([home_currency, rate is not None, amount_home is not None])
        if multi_used and (not home_currency or rate is None):
            flash("If you use home conversion, please provide Home Currency and Exchange Rate.", "error")
            return render_template("add_transaction.html")

        # Optional compute home amount
        if multi_used and amount_home is None and rate is not None:
            amount_home: Decimal | None = (amount * rate).quantize(Decimal("0.01"))

        debug_payload: dict[str, object] = {
            "amount": amount,
            "currency": currency,
            "type": txn_type,
            "category": category,
            "note": note,
            "date_paid": date_paid_obj,
            "period_month": period_month_obj,
            "home_currency": home_currency,
            "exchange_rate": rate,
            "amount_home": amount_home,
        }

        print(debug_payload)
        return redirect(url_for("main.home"))
    return render_template("add_transaction.html")
