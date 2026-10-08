from decimal import Decimal

import pytest
from flask import Flask
from sqlalchemy.exc import IntegrityError

from app.models import Account, AccountBalanceEvent, User, db


def test_zero_opening_event_is_allowed(app: Flask, user: User) -> None:
    with app.app_context():
        # Arrange: Create an account with zero balance.
        account = Account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            balance=Decimal("0.00"),
        )

        # Arrange: Create its opening event.
        event = AccountBalanceEvent(
            account=account,
            event_type="opening",
            amount=Decimal("0.00"),
            balance_before=None,
            balance_after=Decimal("0.00"),
            reason="Account initialized",
        )

        # Act: Persist both objects.
        db.session.add_all([account, event])
        db.session.commit()

        # Assert: Retrieve the saved event.
        saved_event = db.session.get(
            AccountBalanceEvent,
            event.id,
        )

        assert saved_event is not None
        assert saved_event.event_type == "opening"
        assert saved_event.amount == Decimal("0.00")
        assert saved_event.balance_before is None
        assert saved_event.balance_after == Decimal("0.00")
        assert saved_event.account_id == account.id


def test_inconsistent_correction_is_rejected(app: Flask, user: User) -> None:
    with app.app_context():
        account = Account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            balance=Decimal("8000.00"),
        )

        event = AccountBalanceEvent(
            account=account,
            event_type="correction",
            amount=Decimal("-500.00"),
            balance_before=Decimal("8000.00"),
            balance_after=Decimal("8000.00"),  # Intentionally wrong! (The invalid relationship is -> 8000 + (-500) is not equal to 8000)
            reason="Opening balance correction",
        )

        with pytest.raises(IntegrityError):
            db.session.add_all([account, event])
            db.session.commit()

        db.session.rollback()