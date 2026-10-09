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


def test_negative_opening_amount_is_rejected(app: Flask, user: User) -> None:
    with app.app_context():
        # Arrange: Create a valid account.
        account = Account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            balance=Decimal("0.00"),
        )

        db.session.add(account)
        db.session.commit()

        # Arrange: Create an invalid opening event.
        event = AccountBalanceEvent(
            account=account,
            event_type="opening",
            amount=Decimal("-100.00"),
            balance_before=None,
            balance_after=Decimal("-100.00"),
            reason="Invalid negative opening balance",
        )

        # Act: Database must reject the event.
        with pytest.raises(IntegrityError):
            db.session.add(event)
            db.session.commit()

        db.session.rollback()

        # Assert: No event was saved.
        saved_event = db.session.query(AccountBalanceEvent).filter_by(account_id=account.id).first()
        assert saved_event is None


def test_opening_event_requires_null_previous_balance(app: Flask, user: User) -> None:
    with app.app_context():
        account = Account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            balance=Decimal("0.00"),
        )
        event = AccountBalanceEvent(
            account=account,
            event_type="opening",
            amount=Decimal("100.00"),
            balance_before=Decimal("0.00"),
            balance_after=Decimal("100.00"),
            reason="Account initialized with null balance",
        )

        with pytest.raises(IntegrityError):
            db.session.add_all([account, event])
            db.session.commit()
        db.session.rollback()


def test_valid_correction_is_allowed(app: Flask, user: User) -> None:
    with app.app_context():
        account = Account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            balance=Decimal("7500.00"),
        )
        event = AccountBalanceEvent(
            account=account,
            event_type="correction",
            amount=Decimal("-500.00"),
            balance_before=Decimal("8000.00"),
            balance_after=Decimal("7500.00"),
            reason="Opening balance correction",
        )

        db.session.add_all([account, event])
        db.session.commit()
        saved_event = db.session.get(AccountBalanceEvent, event.id)

        assert saved_event is not None
        assert saved_event.event_type == "correction"
        assert saved_event.amount == Decimal("-500.00")
        assert saved_event.balance_before == Decimal("8000.00")
        assert saved_event.balance_after == Decimal("7500.00")
        assert saved_event.account_id == account.id


def test_duplicate_opening_event_is_rejected(app: Flask, user: User) -> None:
    # 1. Create valid Account
    account = Account(
        user_id=user.id,
        account_type="checking",
        currency="TRY",
        balance=Decimal("0.00"),
    )
    # 2. Commit Account
    db.session.add(account)
    db.session.commit()

    # 3. Create first opening event with valid values
    first_event = AccountBalanceEvent(
        account_id=account.id,
        event_type="opening",
        amount=Decimal("0.00"),
        balance_before=None,
        balance_after=Decimal("0.00"),
        reason="Account initialized with first opening balance",
    )
    # 4. Commit successfully
    db.session.add(first_event)
    db.session.commit()

    # 5. Create second opening event with identical valid values
    second_event = AccountBalanceEvent(
        account_id=account.id,
        event_type="opening",
        amount=Decimal("0.00"),
        balance_before=None,
        balance_after=Decimal("0.00"),
        reason="Account initialized with duplicate opening balance",
    )

    # 6. Attempt commit & 7. IntegrityError expected
    with pytest.raises(IntegrityError):
        db.session.add(second_event)
        db.session.commit()

    # 8. Rollback
    db.session.rollback()

    # 9. Verify only one opening event exists in the database
    remaining_events = (
        db.session.query(AccountBalanceEvent)
        .filter_by(account_id=account.id, event_type="opening")
        .all()
    )
    assert len(remaining_events) == 1
    assert remaining_events[0].id == first_event.id

