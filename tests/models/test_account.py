from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Account, db


# ==========================================
#               Valid account
#
# We want to prove this state is legal:
#
# User
# └── Checking TRY
#       balance = 1000.00
# ==========================================
def test_create_valid_account(app, user) -> None:
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
#
# V1 rule:
# Checking and savings balances cannot
# become negative.
# ==========================================
def test_negative_balance_is_rejected(app, user) -> None:
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
# V1 supports:
#   checking
#   savings
#
# Other account types must be rejected.
# ==========================================
def test_invalid_account_type_is_rejected(app, user) -> None:
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
# ├── Checking TRY   <- allowed
# └── Checking TRY   <- rejected
#
# Unique identity:
# (user_id, account_type, currency)
# ==========================================
def test_duplicate_account_is_rejected(app, user) -> None:
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