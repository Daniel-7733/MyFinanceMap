"""
                            *************************************

                                        routes only
                              connects user actions to services

                            *************************************
"""
from flask import Blueprint, render_template, request, redirect, url_for, Response, flash
from decimal import Decimal, InvalidOperation
from datetime import date, datetime
from .models import Transaction, db
from .services.summary import get_balance


MAIN_CURRENCY: str = "USD"  # later: load from user settings / config


main: Blueprint = Blueprint("main", __name__)



@main.context_processor
def inject_current_year() -> dict[str, int]:
    """
    This function automatically update the year of footer for copy right in base.html
    :return: current year
    """
    return {"current_year": datetime.now().year}

@main.route("/")
def home() -> str:
    """
    :return: home page
    """
    transactions: list[Transaction] = Transaction.query.order_by(Transaction.id.desc()).all()
    balance: Decimal = get_balance(transactions)

    return render_template(
        "index.html",
        amount=f"You have {balance:,.2f} USD", # TODO: Currency will be user main currency; the main currency that everything is change to it
        transactions=transactions
    )



@main.route("/transactions", methods=["GET", "POST"])
def add_transaction() -> Response | str:
    if request.method == "POST":
        # --- amount ---
        amount_raw: str = request.form.get("amount", "").strip()
        try:
            amount: Decimal = Decimal(amount_raw).quantize(Decimal("0.01"))
        except (InvalidOperation, TypeError):
            flash("Amount must be a valid number like 19.00", "error")
            return render_template("add_transaction.html")

        # --- currency ---
        currency: str = request.form.get("currency_code", "").strip().upper()
        if not currency:
            flash("Please select a currency.", "error")
            return render_template("add_transaction.html")

        # --- type/category/note ---
        txn_type: str = request.form.get("txn_type", "").strip()
        category: str = request.form.get("category", "").strip()
        note: str = request.form.get("note", "").strip() or None

        # --- method  ---
        method: str = request.form.get("method", "").strip()

        # --- dates ---
        date_paid_raw: str = request.form.get("date_paid", "").strip()
        period_month_raw: str = request.form.get("period_month", "").strip()

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

        # --- rate rule: only required when foreign currency ---
        rate: Decimal | None = None
        rate_raw: str = request.form.get("exchange_rate", "").strip()

        is_foreign: bool = (currency != MAIN_CURRENCY)

        if is_foreign:
            if not rate_raw:
                flash(f"Exchange rate is required when currency is not {MAIN_CURRENCY}.", "error")
                return render_template("add_transaction.html")

            try:
                rate = Decimal(rate_raw)
            except (InvalidOperation, TypeError):
                flash("Exchange rate must be a valid number like 1.25", "error")
                return render_template("add_transaction.html")

            if rate <= 0:
                flash("Exchange rate must be greater than 0.", "error")
                return render_template("add_transaction.html")

        # (optional) compute home amount for reporting
        amount_home: Decimal = (amount * rate).quantize(Decimal("0.01")) if (is_foreign and rate) else amount

        transaction = Transaction(
            txn_type=txn_type,
            amount=amount,
            currency=currency,
            category=category,
            note=note,
            date_paid=date_paid_obj,
            period_month=period_month_obj,
            exchange_rate_to_home=rate,    # store None for main currency
            amount_home=amount_home,       # always stored in home currency
            method=method
        )

        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for("main.home"))

    return render_template("add_transaction.html")

