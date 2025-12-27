from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

db: SQLAlchemy = SQLAlchemy()


class Transaction(db.Model):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    txn_type: Mapped[str] = mapped_column(nullable=False)  # "income" or "expense"

    amount: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(nullable=False)  # "USD", "EUR", ...

    home_currency: Mapped[str | None] = mapped_column(nullable=True)  # optional for MVP
    exchange_rate_to_home: Mapped[Decimal | None] = mapped_column(db.Numeric(18, 8), nullable=True)
    amount_home: Mapped[Decimal | None] = mapped_column(db.Numeric(12, 2), nullable=True)

    category: Mapped[str] = mapped_column(nullable=False)
    note: Mapped[str | None] = mapped_column(nullable=True)

    date_paid: Mapped[date] = mapped_column(nullable=False)
    period_month: Mapped[date] = mapped_column(nullable=False)  # store as first day of month

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False) # Store the real time and user can't change it

    __table_args__ = (
        CheckConstraint("txn_type IN ('income', 'expense')", name="ck_transactions_type"),
        CheckConstraint("amount >= 0", name="ck_transactions_amount_nonnegative"),
        CheckConstraint("amount_home IS NULL OR amount_home >= 0", name="ck_transactions_amount_home_nonnegative"),
        CheckConstraint(
            "exchange_rate_to_home IS NULL OR exchange_rate_to_home > 0",
            name="ck_transactions_rate_positive"
        ),
    )
