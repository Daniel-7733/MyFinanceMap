from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional

from flask import flash
from ..models import Transaction
from app.constants import MONEY_2DP



@dataclass(frozen=True)
class ParsedTxn:
    txn_type: str
    amount: Decimal
    currency: str
    category: str
    note: str | None
    method: str
    date_paid: date
    period_month: date
    exchange_rate_to_home: Decimal | None
    amount_home: Decimal


def _parse_money_2dp(raw: str, field_name: str) -> Optional[Decimal]:
    raw = (raw or "").strip()
    try:
        return Decimal(raw).quantize(MONEY_2DP)
    except (InvalidOperation, TypeError):
        flash(f"{field_name} must be a valid number like 19.00", "error")
        return None


def _parse_rate(raw: str) -> Optional[Decimal]:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        rate = Decimal(raw)
    except (InvalidOperation, TypeError):
        flash("Exchange rate must be a valid number like 1.25", "error")
        return None
    if rate <= 0:
        flash("Exchange rate must be greater than 0.", "error")
        return None
    return rate


def _parse_date_paid(raw: str) -> Optional[date]:
    raw = (raw or "").strip()
    if not raw:
        return date.today()
    try:
        return date.fromisoformat(raw)
    except ValueError:
        flash("Date Paid must be a valid date.", "error")
        return None


def _parse_period_month(raw: str) -> Optional[date]:
    raw = (raw or "").strip()
    try:
        year_str, mon_str = raw.split("-")
        return date(int(year_str), int(mon_str), 1)
    except Exception:
        flash("Period Month must be a valid month.", "error")
        return None


def parse_transaction_form(form, main_currency: str) -> ParsedTxn | None:
    """
    Parse + validate the transaction form.
    Returns ParsedTxn or None (and flashes errors).
    """
    amount = _parse_money_2dp(form.get("amount", ""), "Amount")
    if amount is None:
        return None

    currency = (form.get("currency_code", "") or "").strip().upper()
    if not currency:
        flash("Please select a currency.", "error")
        return None

    txn_type = (form.get("txn_type", "") or "").strip()
    category = (form.get("category", "") or "").strip()
    note = (form.get("note", "") or "").strip() or None
    method = (form.get("method", "") or "").strip()

    date_paid = _parse_date_paid(form.get("date_paid", ""))
    if date_paid is None:
        return None

    period_month = _parse_period_month(form.get("period_month", ""))
    if period_month is None:
        return None

    is_foreign = currency != main_currency

    rate_raw = form.get("exchange_rate", "")
    rate = _parse_rate(rate_raw)

    if is_foreign and rate is None:
        flash(f"Exchange rate is required when currency is not {main_currency}.", "error")
        return None

    amount_home = (amount * rate).quantize(MONEY_2DP) if (is_foreign and rate) else amount

    return ParsedTxn(
        txn_type=txn_type,
        amount=amount,
        currency=currency,
        category=category,
        note=note,
        method=method,
        date_paid=date_paid,
        period_month=period_month,
        exchange_rate_to_home=rate if is_foreign else None,
        amount_home=amount_home,
    )


def apply_parsed_to_model(txn: Transaction, parsed: ParsedTxn) -> None:
    """Mutate an existing Transaction from ParsedTxn."""
    txn.txn_type = parsed.txn_type
    txn.amount = parsed.amount
    txn.currency = parsed.currency
    txn.category = parsed.category
    txn.note = parsed.note
    txn.method = parsed.method
    txn.date_paid = parsed.date_paid
    txn.period_month = parsed.period_month
    txn.exchange_rate_to_home = parsed.exchange_rate_to_home
    txn.amount_home = parsed.amount_home
