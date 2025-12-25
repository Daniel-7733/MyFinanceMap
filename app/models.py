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
    type: Mapped[str] = mapped_column(nullable=False)                          # "income" or "expense"
    amount: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), nullable=False) # Use Numeric so DB stores exact decimals (not float)
    category: Mapped[str] = mapped_column(nullable=False)
    note: Mapped[str | None] = mapped_column(nullable=True)
    date_paid: Mapped[date] = mapped_column(nullable=False)                    # When the money actually happened (bank/cash date)
    period_month: Mapped[date] = mapped_column(nullable=False)                 # Which month this transaction belongs to (store as first day of month)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("type IN ('income', 'expense')", name="ck_transactions_type"),
        CheckConstraint("amount >= 0", name="ck_transactions_amount_nonnegative"),
    )
