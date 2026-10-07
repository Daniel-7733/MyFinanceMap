"""
stronger matrix test:

                    ACCOUNT INVARIANTS

                     Should DB allow?
                           │
          ┌────────────────┴────────────────┐
          │                                 │
        YES                                NO
          │                                 │
    balance = 0 ✓                    balance = -1 ✗
    checking TRY ✓                  investment ✗
    checking + savings TRY ✓        duplicate checking TRY ✗
    checking TRY + CAD ✓
    same account, different users ✓
"""

from decimal import Decimal

import pytest
from flask import Flask
from sqlalchemy.exc import IntegrityError

from app.models import Account, User, db


# ==========================================
#               Valid account
#
# User
# └── Checking TRY
#       balance = 1000.00
# ==========================================
def test_create_valid_account(app: Flask, user: User) -> None:
    with app.app_context():
        account = Account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            balance=Decimal("1000.00"),
        )

        db.session.add(account)
        db.session.commit()

        assert account.user_id == user.id
        assert account.account_type == "checking"
        assert account.currency == "TRY"
        assert account.balance == Decimal("1000.00")


# ==========================================
#        Negative balance must fail
#
# Checking TRY
# balance = -1.00
# ==========================================
def test_negative_balance_is_rejected(
    app: Flask,
    user: User,
) -> None:
    with app.app_context():
        account = Account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            balance=Decimal("-1.00"),
        )

        db.session.add(account)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# ==========================================
#       Invalid account type must fail
#
# checking   ✓
# savings    ✓
# investment ✗
# ==========================================
def test_invalid_account_type_is_rejected(
    app: Flask,
    user: User,
) -> None:
    with app.app_context():
        account = Account(
            user_id=user.id,
            account_type="investment",
            currency="TRY",
            balance=Decimal("1000.00"),
        )

        db.session.add(account)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# ==========================================
#        Duplicate account must fail
#
# User
# ├── Checking TRY   ✓
# └── Checking TRY   ✗
#
# Unique:
# (user_id, account_type, currency)
# ==========================================
def test_duplicate_account_is_rejected(
    app: Flask,
    user: User,
) -> None:
    with app.app_context():
        first_account = Account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            balance=Decimal("1000.00"),
        )

        db.session.add(first_account)
        db.session.commit()

        second_account = Account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            balance=Decimal("500.00"),
        )

        db.session.add(second_account)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# ==========================================
#        Zero balance is valid
# balance >= 0  not balance > 0
# ==========================================
def test_zero_balance_is_allowed(
    app: Flask,
    user: User,
) -> None:
    with app.app_context():
        account = Account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            balance=Decimal("0.00"),
        )

        db.session.add(account)
        db.session.commit()

        assert account.balance == Decimal("0.00")


# ==========================================
# Same currency can have checking + savings
# User
# ├── Checking TRY  ✓
# └── Savings  TRY  ✓
#
# because uniqueness is the combination:
# (user_id, account_type, currency)
# ==========================================
def test_same_currency_different_account_types_are_allowed(
    app: Flask,
    user: User,
) -> None:
    with app.app_context():
        checking = Account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            balance=Decimal("1000.00"),
        )

        savings = Account(
            user_id=user.id,
            account_type="savings",
            currency="TRY",
            balance=Decimal("500.00"),
        )

        db.session.add_all([checking, savings])
        db.session.commit()

        assert checking.currency == savings.currency
        assert checking.account_type != savings.account_type


# ==========================================
# Same account type can exist in different currencies
# User
# ├── Checking TRY  ✓
# └── Checking CAD  ✓
# ==========================================
def test_same_account_type_different_currencies_are_allowed(
    app: Flask,
    user: User,
) -> None:
    with app.app_context():
        try_account = Account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            balance=Decimal("1000.00"),
        )

        cad_account = Account(
            user_id=user.id,
            account_type="checking",
            currency="CAD",
            balance=Decimal("100.00"),
        )

        db.session.add_all([try_account, cad_account])
        db.session.commit()

        assert try_account.account_type == cad_account.account_type
        assert try_account.currency != cad_account.currency


# ==========================================
# Different users can have the same account combination
#
# Our uniqueness rule is:
# Daniel → Checking TRY ✓
# Sara   → Checking TRY ✓
# ==========================================
def test_different_users_can_have_same_account_type_and_currency(
    app: Flask,
    user: User,
) -> None:
    with app.app_context():
        second_user = User(
            username="second_user",
            email="second@example.com",
            password_hash="test-hash",
            home_currency="TRY",
            location="Test",
        )

        db.session.add(second_user)
        db.session.commit()

        first_account = Account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            balance=Decimal("1000.00"),
        )

        second_account = Account(
            user_id=second_user.id,
            account_type="checking",
            currency="TRY",
            balance=Decimal("500.00"),
        )

        db.session.add_all([first_account, second_account])
        db.session.commit()

        assert first_account.user_id != second_account.user_id

