"""
Our Future schema is now taking shape
                         User
                          │
          ┌───────────────┴────────────────┐
          │                                │
          ▼                                ▼
      Accounts                       Transactions
          │                                │
          │                                │
 ┌────────┼────────┐                       │
 ▼        ▼        ▼                       │
Checking Savings Checking                  │
 TRY      TRY      CAD                     │
 │         │                               │
 └────┬────┘                               │
      │                                    │
      ▼                                    │
   Transfers                               │
      │                                    │
      └──────────── HISTORY ────────────────┘
                         │
                         ▼
                     Analytics
                         │
                         ▼
             Financial Intelligence


             The ownership
            User
             │
             │ 1
             │
             └──────────────┐
                            │
                            ▼ many
                         Account
                            │
                    ┌───────┼─────────┐
                    ▼       ▼         ▼
                 checking   TRY    1000.00


---------------- relationships ----------------
                    User
                    ├── transactions ──────► Transaction
                    │                         │
                    │                         └── user ──► User
                    │
                    └── accounts ───────────► Account
                                              │
                                              └── user ──► User
"""


from datetime import date, datetime
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.finance import compute_home_amount
from flask_login import UserMixin


db: SQLAlchemy = SQLAlchemy()

class Transaction(db.Model):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    txn_type: Mapped[str] = mapped_column(String(7), nullable=False)         # income/expense
    amount: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)         # USD/EUR/TRY

    exchange_rate_to_home: Mapped[Decimal | None] = mapped_column(db.Numeric(18, 8), nullable=True)
    amount_home: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), nullable=False)

    category: Mapped[str] = mapped_column(String(30), nullable=False)
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)

    date_paid: Mapped[date] = mapped_column(nullable=False)
    period_month: Mapped[date] = mapped_column(nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    # ------------------- Relationship to User ------------------ #
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="transactions")
    # ------------------------------------------------------------ #

    __table_args__ = (
        CheckConstraint("txn_type IN ('income', 'expense')", name="ck_transactions_type"),
        CheckConstraint("amount >= 0", name="ck_transactions_amount_nonnegative"),
        CheckConstraint("amount_home >= 0", name="ck_transactions_amount_home_nonnegative"),
        CheckConstraint("exchange_rate_to_home IS NULL OR exchange_rate_to_home > 0", name="ck_transactions_rate_positive"),
        CheckConstraint("method IN ('card', 'cash', 'bank_transfer')", name="ck_transactions_method"),
    )

    def sync_amount_home(self, main_currency: str) -> None:
        self.amount_home = compute_home_amount(
            self.amount,
            self.currency,
            self.exchange_rate_to_home,
            main_currency,
        )


class Account(db.Model):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_type: Mapped[str] = mapped_column(String(10), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="accounts")

    # ----------------------- relationship ---------------------- #
    balance_events = relationship(
        "AccountBalanceEvent",
        back_populates="account",
    )
    # ------------------------------------------------------------ #

    __table_args__ = (
        CheckConstraint(
            "account_type IN ('checking', 'savings')",
            name="ck_accounts_type",
        ),
        CheckConstraint(
            "balance >= 0",
            name="ck_accounts_balance_nonnegative",
        ),
        UniqueConstraint(
            "user_id",
            "account_type",
            "currency",
            name="uq_accounts_user_type_currency",
        ),
    )


class AccountBalanceEvent(db.Model):
    __tablename__ = "account_balance_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), nullable=False)
    balance_before: Mapped[Decimal | None] = mapped_column(db.Numeric(12, 2), nullable=True)
    balance_after: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), nullable=False)
    reason: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    # ----------------------- relationship ---------------------- #
    account = relationship("Account", back_populates="balance_events")
    # ------------------------------------------------------------ #

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('opening', 'correction')",
            name="ck_balance_events_type",
        ),
        CheckConstraint(
            "balance_after >= 0",
            name="ck_balance_events_after_nonnegative",
        ),
        CheckConstraint(
            "balance_before IS NULL OR balance_before >= 0",
            name="ck_balance_events_before_nonnegative",
        ),
        CheckConstraint(
            """
            (
                event_type = 'opening'
                AND balance_before IS NULL
                AND amount >= 0
                AND balance_after = amount
            )
            OR
            (
                event_type = 'correction'
                AND balance_before IS NOT NULL
                AND balance_after = balance_before + amount
            )
            """,
            name="ck_balance_events_consistency",
        ),
        Index(
            "uq_balance_events_one_opening_per_account",
            "account_id",
            unique=True,
            sqlite_where=text("event_type = 'opening'"),
        ),
    )


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    home_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    # Relationship
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
