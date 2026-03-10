"""
                            *************************************

                                        routes only
                              connects user actions to services
                                transactions CRUD + dashboard

                            *************************************
"""
from __future__ import annotations

from typing import Any
from datetime import datetime
from decimal import Decimal

from flask import Blueprint, render_template, request, redirect, url_for, Response, flash
from flask_login import login_required, current_user

from sqlalchemy.orm import Query

from .models import Transaction, db
from .services.analytics import monthly_totals, category_totals, monthly_income_expense_series, monthly_income_expense_date_series, category_expense_totals, split_bucket_totals
from .services.budgeting import available_balance, deficit_amount, total_income, total_expense, calculate_503020, rule_503020_from_actual, split_income_expense
from .services.summary import get_finance_overview, get_balance, get_income_expense_net
from .core.dates import get_current_month

from .services.transactions import parse_transaction_form, apply_parsed_to_model, get_user_transactions, \
    current_user_transactions_query
from .services.filters import select_month, get_available_months



main: Blueprint = Blueprint("main", __name__)



@main.route("/whoami")
def whoami() -> str:
    """For Debug purposes"""
    return f"authenticated={current_user.is_authenticated}, id={getattr(current_user,'id',None)}"


@main.context_processor
def inject_globals() -> dict[str, int | str]:
    """
    Inject common template variables:
    - current_year
    - user's main currency
    """
    data = {
        "current_year": datetime.now().year,
    }

    if current_user.is_authenticated:
        data["MAIN_CURRENCY"] = current_user.home_currency
    else:
        data["MAIN_CURRENCY"] = "USD"

    return data


@main.route("/")
@login_required
def home() -> str:
    _, _, available, deficit = get_finance_overview()
    return render_template(
        "index.html",
        available=f"{available:,.2f}",
        deficit=f"{deficit:,.2f}",
        currency=current_user.home_currency,
    )


@main.route("/transactions-add", methods=["GET", "POST"])
@login_required
def add_transaction() -> Response | str:
    if request.method == "POST":
        parsed = parse_transaction_form(request.form, current_user.home_currency)
        if parsed is None:
            return render_template("add_transaction.html")

        txn = Transaction(
            txn_type=parsed.txn_type,
            amount=parsed.amount,
            currency=parsed.currency,
            category=parsed.category,
            note=parsed.note,
            date_paid=parsed.date_paid,
            period_month=parsed.period_month,
            exchange_rate_to_home=parsed.exchange_rate_to_home,
            amount_home=parsed.amount_home,
            method=parsed.method,
            user_id=current_user.id,
        )
        txn.sync_amount_home(current_user.home_currency)
        db.session.add(txn)
        db.session.commit()
        return redirect(url_for("main.show_transactions"))

    return render_template("add_transaction.html", user_currency=current_user.home_currency)


@main.route("/transactions", methods=["GET"])
@login_required
def show_transactions() -> str:
    month_str: str | None = request.args.get("month")  # "YYYY-MM" or "all"

    # dropdown options need all months
    # all_transactions: list[Transaction] = Transaction.query.order_by(Transaction.id.desc()).all()
    all_transactions: list[Transaction] = get_user_transactions()
    month_options: dict[str, str] = get_available_months(all_transactions)
    today_key, today_label = get_current_month()

    selection = select_month(month_str, today_key, month_options)

    query: Query[Transaction] = current_user_transactions_query().order_by(Transaction.id.desc())
    if selection.period_month:
        query = query.filter(Transaction.period_month == selection.period_month)

    transactions: list[Transaction] = query.all()

    incomes, expenses = split_income_expense(transactions)
    income: Decimal = total_income(incomes)
    expense: Decimal = total_expense(expenses)

    balance: Decimal = get_balance(transactions)
    available: Decimal = available_balance(balance)
    deficit: Decimal = deficit_amount(balance)

    return render_template(
        "transactions.html",
        transactions=transactions,
        income=f"{income:,.2f}",
        expense=f"{expense:,.2f}",
        available=f"{available:,.2f}",
        deficit=f"{deficit:,.2f}",
        currency=current_user.home_currency,
        month_options=month_options,
        today_key=today_key,
        today_label=today_label,
        selected_month=selection.month_key,
        selected_label=selection.label,
    )


@main.route("/transactions-edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_transaction(id: int) -> Response | str:
    txn: Transaction = Transaction.query.get_or_404(id)

    if request.method == "POST":
        parsed = parse_transaction_form(request.form, current_user.home_currency)
        if parsed is None:
            return render_template("edit_transaction.html", transaction=txn, id=id)

        apply_parsed_to_model(txn, parsed)
        txn.sync_amount_home(current_user.home_currency)
        db.session.commit()
        flash("Transaction updated.", "success")
        return redirect(url_for("main.show_transactions"))

    return render_template("edit_transaction.html", transaction=txn, id=id)


@main.route("/transactions-delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete_transaction(id: int) -> Response | str:
    txn: Transaction = Transaction.query.get_or_404(id)

    if request.method == "POST":
        db.session.delete(txn)
        db.session.commit()
        flash("Transaction deleted.", "success")
        return redirect(url_for("main.show_transactions"))

    return render_template("delete_transaction.html", transaction=txn, id=id)


@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard() -> str:
    # dropdown options
    all_transactions: list[Transaction] =  get_user_transactions()
    month_options: dict[str, str] = get_available_months(all_transactions)
    today_key, today_label = get_current_month()

    # month selection
    month_str: str | None = request.args.get("month")  # "YYYY-MM" or "all"
    selection = select_month(month_str, today_key, month_options)

    query: Query[Transaction] = current_user_transactions_query().order_by(Transaction.id.desc())
    if selection.period_month:
        query = query.filter(Transaction.period_month == selection.period_month)

    transactions: list[Transaction] = query.all()

    series: dict[str, list] = monthly_income_expense_series(transactions)
    different_series: dict[str, list] = monthly_income_expense_date_series(transactions)
    expense_category = category_expense_totals(transactions)

    # --- 50/30/20 targets (based on income) ---
    income_total, expense_total, net = get_income_expense_net(transactions)
    targets: dict[str, Decimal] = calculate_503020(income_total)  # {"needs":..., "wants":..., "savings":...}
    budgeting_rule: dict[str, list[str] | list[float]] = {
        "labels": ["Needs (50%)", "Wants (30%)", "Savings (20%)"],
        "values": [float(targets["needs"]), float(targets["wants"]), float(targets["savings"])],
    }

    # --- 50/30/20 actual spending breakdown (based on categories) ---
    bucket: dict[str, Decimal] = split_bucket_totals(transactions)

    needs_spend: Decimal = bucket.get("needs", Decimal("0"))
    wants_spend: Decimal = bucket.get("wants", Decimal("0"))
    savings_spend: Decimal = bucket.get("savings", Decimal("0"))

    leftover: Decimal = max(
        Decimal("0"),
        income_total - (needs_spend + wants_spend + savings_spend)
    )

    rule: dict[str, Decimal] = rule_503020_from_actual(
        income=income_total,
        needs=needs_spend,
        wants=wants_spend,
        savings=leftover,
    )

    need_p: float = float(rule["needs_percentage"])
    want_p: float = float(rule["wants_percentage"])
    save_p: float = float(rule["savings_percentage"])

    actual_pie: dict[str, list[str] | list[float]] = {
        "labels": [
            f"Needs (spent) {need_p:.2f}%",
            f"Wants (spent) {want_p:.2f}%",
            f"Savings (left) {save_p:.2f}%",
        ],
        "values": [
            float(needs_spend),
            float(wants_spend),
            float(leftover),
        ],
    }
    # --------------------------------------------------

    # totals
    balance: Decimal = get_balance(transactions)
    available: Decimal = available_balance(balance)
    deficit: Decimal = deficit_amount(balance)

    # category totals (only for a specific month)
    category_data: list[dict] = []
    if selection.period_month:
        category_data = category_totals(transactions, selection.period_month)

    # last_n chart
    last_n_str: str = request.args.get("last_n", "6")
    try:
        last_n: int = int(last_n_str)
    except ValueError:
        last_n = 6

    month_data: list[dict[str, Any]] = monthly_totals(user_id=current_user.id, last_n=last_n)

    return render_template(
        "dashboard.html",
        transactions=transactions,
        balance=f"{balance:,.2f}",
        available=f"{available:,.2f}",
        deficit=f"{deficit:,.2f}",
        currency=current_user.home_currency,
        month_data=month_data,
        category_data=category_data,
        last_n=last_n,
        month_options=month_options,
        today_key=today_key,
        today_label=today_label,
        selected_month=selection.month_key,
        selected_label=selection.label,
        chart_data=series,
        different_chart_data=different_series,
        expense_category=expense_category,
        budgeting_rule=budgeting_rule,     # for pie chart target
        actual_pie=actual_pie,             # actual totals
        rule=rule,                         # actual percentages vs target
        )
