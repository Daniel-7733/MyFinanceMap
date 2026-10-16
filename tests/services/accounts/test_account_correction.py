from decimal import Decimal

import pytest
from flask import Flask
from sqlalchemy import select, func
from app.models import Account, AccountBalanceEvent, Transaction, User, db
from app.services.accounts.account_service import create_account, correct_account_balance


def test_correct_account_balance_downward(app: Flask, user: User) -> None:
    with app.app_context():

        # ARRANGE: Create an account with 10,000 TRY.
        account = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("10000.00"),
        )

        # ACT: Correct its balance to 9,700 TRY.
        correct_account_balance(
            user_id=user.id,
            account_id=account.id,
            new_balance=Decimal("9700.00"),
            reason="Bank reconciliation",
        )

        # ASSERT: Verify the new balance.
        db.session.expire_all()
        saved_account = db.session.get(Account, account.id)

        assert saved_account is not None
        assert saved_account.balance == Decimal("9700.00")

        # ASSERT: Retrieve the account's audit history.
        events = db.session.scalars(
            select(AccountBalanceEvent)
            .where(AccountBalanceEvent.account_id == account.id)
            .order_by(AccountBalanceEvent.id)
        ).all()

        assert len(events) == 2

        opening_event = events[0]
        correction_event = events[1]

        # Original history must remain unchanged.
        assert opening_event.event_type == "opening"
        assert opening_event.amount == Decimal("10000.00")
        assert opening_event.balance_after == Decimal("10000.00")

        # Verify the signed correction.
        assert correction_event.event_type == "correction"
        assert correction_event.amount == Decimal("-300.00")
        assert correction_event.balance_before == Decimal("10000.00")
        assert correction_event.balance_after == Decimal("9700.00")
        assert correction_event.reason == "Bank reconciliation"

        # A balance correction is not income or expense.
        transaction_count = db.session.scalar(
            select(func.count()).select_from(Transaction)
        )

        assert transaction_count == 0


# B. Return the Account without creating a new event. Here is the road map:
# [1] The Account balance remains 5,000 TRY.
# [2] The Account ID remains unchanged.
# [3] Exactly one balance event exists (the opening event).
# [4] No correction event is created.
# [5] No income or expense Transaction is created.
# 5 of 5 assertions checked
def test_correction_with_unchanged_balance(app: Flask, user: User) -> None:
    with app.app_context():
        account = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("5000.00"),
        )

        result = correct_account_balance(
            user_id=user.id,
            account_id=account.id,
            new_balance=Decimal("5000.00"),
            reason="No balance correction",
        )

        assert result.id == account.id

        db.session.expire_all()
        saved_account = db.session.get(Account, account.id)

        assert saved_account is not None
        assert saved_account.id == account.id
        assert saved_account.balance == Decimal("5000.00")

        events = db.session.scalars(
            select(AccountBalanceEvent)
            .where(AccountBalanceEvent.account_id == account.id)
            .order_by(AccountBalanceEvent.id)
        ).all()

        assert len(events) == 1

        opening_event = events[0]

        assert opening_event.event_type == "opening"
        assert opening_event.amount == Decimal("5000.00")
        assert opening_event.balance_before is None
        assert opening_event.balance_after == Decimal("5000.00")

        transaction_count = db.session.scalar(
            select(func.count()).select_from(Transaction)
        )
        assert transaction_count == 0


def test_cannot_correct_another_users_account(app: Flask, user: User) -> None:
    with app.app_context():

        # ARRANGE: Create another real database user.
        other_user = User(
            username="other_user",
            email="other@example.com",
            password_hash="test-hash",
            home_currency="TRY",
            location="Test",
        )

        db.session.add(other_user)
        db.session.commit()

        # ARRANGE: Original user creates an account.
        account = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("5000.00"),
        )

        # ACT: Other user attempts to correct the account.
        with pytest.raises(LookupError, match="Account does not exist or does not belong to user"):
            correct_account_balance(
                user_id=other_user.id, # Intentionally, add different user id
                account_id=account.id, # Use correct account id which has different user id
                new_balance=Decimal("1000.00"),
                reason="Unauthorized correction",
            )

        # ASSERT: The account was not modified.
        db.session.expire_all()
        saved_account = db.session.get(Account, account.id)

        assert saved_account is not None
        assert saved_account.balance == Decimal("5000.00")
        assert saved_account.user_id == user.id

        # ASSERT: No correction event was created.
        events = db.session.scalars(
            select(AccountBalanceEvent)
            .where(AccountBalanceEvent.account_id == account.id)
        ).all()

        assert len(events) == 1
        assert events[0].event_type == "opening"

