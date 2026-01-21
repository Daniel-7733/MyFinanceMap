"""
                            *************************************

                                        routes only
                              connects user actions to services

                            *************************************
"""
from flask import Blueprint, render_template, request, redirect, url_for, Response, flash
from decimal import Decimal, InvalidOperation
from datetime import date, datetime
from sqlalchemy.orm import Query
from .models import Transaction, db
from .services.budgeting import available_balance, deficit_amount
from .services.summary import get_finance_overview, get_balance
from .utils import get_available_months, get_current_month

main: Blueprint = Blueprint("main", __name__)


MAIN_CURRENCY: str = "USD"  # TODO: (later) load from user settings / config



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
    transactions, balance, available, deficit = get_finance_overview()
    return render_template(
        "index.html",
        available=f"{available:,.2f}",
        deficit=f"{deficit:,.2f}",
        currency=MAIN_CURRENCY,
    )


@main.route("/transactions-add", methods=["GET", "POST"])
def add_transaction() -> Response | str:
    """
    This function receive transaction's information from HTML & adds transactions to the database.
    """
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
        return redirect(url_for("main.show_transactions"))

    return render_template("add_transaction.html")


@main.route("/transactions", methods=["GET"])
def show_transactions() -> str:
    month_str: str | None = request.args.get("month")  # "YYYY-MM" or "all"

    base_query: Query[Transaction] = Transaction.query.order_by(Transaction.id.desc())
    all_transactions: list[Transaction] = base_query.all()
    month_options: dict[str, str] = get_available_months(all_transactions)

    today_key, today_label = get_current_month()

    query: Query[Transaction] = Transaction.query.order_by(Transaction.id.desc())
    selected_month: str | None = None

    # if user didn’t choose anything → default to current month
    if not month_str:
        month_str = today_key

    if month_str == "all":
        selected_month = "all"
    else:
        try:
            year_str, mon_str = month_str.split("-")
            period_month_obj: date = date(int(year_str), int(mon_str), 1)
            query = query.filter(Transaction.period_month == period_month_obj)
            selected_month = month_str
        except ValueError:
            # fallback: show all
            selected_month = "all"

    transactions: list[Transaction] = query.all()

    balance: Decimal = get_balance(transactions)
    available: Decimal = available_balance(balance)
    deficit: Decimal = deficit_amount(balance)

    return render_template(
        "transactions.html",
        transactions=transactions,
        available=f"{available:,.2f}",
        deficit=f"{deficit:,.2f}",
        selected_month=selected_month,
        month_options=month_options,
        currency=MAIN_CURRENCY,
        today_key=today_key,
        today_label=today_label,
    )




@main.route("/transactions-edit/<int:id>", methods=["GET", "POST"])
def edit_transaction(id: int) -> Response | str:
    """Edit transaction page"""
    transaction: Transaction = Transaction.query.get_or_404(id)

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

        # update fields
        transaction.txn_type = txn_type
        transaction.amount = amount
        transaction.currency = currency
        transaction.category = category
        transaction.note = note
        transaction.date_paid = date_paid_obj
        transaction.period_month = period_month_obj
        transaction.method = method
        transaction.exchange_rate_to_home = rate
        transaction.amount_home = amount_home

        db.session.commit()

        flash("Transaction updated.", "success")
        return redirect(url_for("main.show_transactions"))

    return render_template("edit_transaction.html", transaction=transaction, id=id)


@main.route("/transactions-delete/<int:id>", methods=["GET", "POST"])
def delete_transaction(id: int) -> Response | str:
    """Delete transaction page"""
    transaction: Transaction = Transaction.query.get_or_404(id)

    if request.method == "POST":
        db.session.delete(transaction)
        db.session.commit()
        flash("Transaction updated.", "success")

        return redirect(url_for("main.show_transactions"))
    return render_template("delete_transaction.html", transaction=transaction, id=id)

