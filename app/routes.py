"""
                            *************************************

                                        routes only
                              connects user actions to services

                            *************************************
"""
from __future__ import annotations

from typing import Any
from datetime import datetime
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, Response, flash
from sqlalchemy.orm import Query

from .models import Transaction, db
from .services.analytics import monthly_totals, category_totals, monthly_income_expense_series
from .services.budgeting import available_balance, deficit_amount, total_income, total_expense
from .services.summary import get_finance_overview, get_balance
from .utils import get_available_months, get_current_month, split_income_expense

from .services.transactions import parse_transaction_form, apply_parsed_to_model
from .services.filters import select_month


main: Blueprint = Blueprint("main", __name__)
MAIN_CURRENCY: str = "USD"  # TODO later: user settings / config


@main.context_processor
def inject_current_year() -> dict[str, int]:
    return {"current_year": datetime.now().year}


@main.route("/")
def home() -> str:
    _, _, available, deficit = get_finance_overview()
    return render_template(
        "index.html",
        available=f"{available:,.2f}",
        deficit=f"{deficit:,.2f}",
        currency=MAIN_CURRENCY,
    )


@main.route("/transactions-add", methods=["GET", "POST"])
def add_transaction() -> Response | str:
    if request.method == "POST":
        parsed = parse_transaction_form(request.form, MAIN_CURRENCY)
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
        )
        db.session.add(txn)
        db.session.commit()
        return redirect(url_for("main.show_transactions"))

    return render_template("add_transaction.html")


@main.route("/transactions", methods=["GET"])
def show_transactions() -> str:
    month_str: str | None = request.args.get("month")  # "YYYY-MM" or "all"

    # dropdown options need all months
    all_transactions: list[Transaction] = Transaction.query.order_by(Transaction.id.desc()).all()
    month_options: dict[str, str] = get_available_months(all_transactions)
    today_key, today_label = get_current_month()

    selection = select_month(month_str, today_key, month_options)

    query: Query[Transaction] = Transaction.query.order_by(Transaction.id.desc())
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
        currency=MAIN_CURRENCY,
        month_options=month_options,
        today_key=today_key,
        today_label=today_label,
        selected_month=selection.month_key,
        selected_label=selection.label,
    )


@main.route("/transactions-edit/<int:id>", methods=["GET", "POST"])
def edit_transaction(id: int) -> Response | str:
    txn: Transaction = Transaction.query.get_or_404(id)

    if request.method == "POST":
        parsed = parse_transaction_form(request.form, MAIN_CURRENCY)
        if parsed is None:
            return render_template("edit_transaction.html", transaction=txn, id=id)

        apply_parsed_to_model(txn, parsed)
        db.session.commit()
        flash("Transaction updated.", "success")
        return redirect(url_for("main.show_transactions"))

    return render_template("edit_transaction.html", transaction=txn, id=id)


@main.route("/transactions-delete/<int:id>", methods=["GET", "POST"])
def delete_transaction(id: int) -> Response | str:
    txn: Transaction = Transaction.query.get_or_404(id)

    if request.method == "POST":
        db.session.delete(txn)
        db.session.commit()
        flash("Transaction deleted.", "success")
        return redirect(url_for("main.show_transactions"))

    return render_template("delete_transaction.html", transaction=txn, id=id)


@main.route("/dashboard", methods=["GET"])
def dashboard() -> str:
    # dropdown options
    all_transactions: list[Transaction] = Transaction.query.order_by(Transaction.id.desc()).all()
    month_options: dict[str, str] = get_available_months(all_transactions)
    today_key, today_label = get_current_month()

    # month selection
    month_str: str | None = request.args.get("month")  # "YYYY-MM" or "all"
    selection = select_month(month_str, today_key, month_options)

    query: Query[Transaction] = Transaction.query.order_by(Transaction.id.desc())
    if selection.period_month:
        query = query.filter(Transaction.period_month == selection.period_month)

    transactions: list[Transaction] = query.all()

    series: dict[str, list] = monthly_income_expense_series(transactions)

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

    month_data: list[dict[str, Any]] = monthly_totals(last_n=last_n)

    return render_template(
        "dashboard.html",
        transactions=transactions,
        balance=f"{balance:,.2f}",
        available=f"{available:,.2f}",
        deficit=f"{deficit:,.2f}",
        currency=MAIN_CURRENCY,
        month_data=month_data,
        category_data=category_data,
        last_n=last_n,
        month_options=month_options,
        today_key=today_key,
        today_label=today_label,
        selected_month=selection.month_key,
        selected_label=selection.label,
        chart_data=series,
    )
