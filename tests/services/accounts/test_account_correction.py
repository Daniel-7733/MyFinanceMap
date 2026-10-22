from decimal import Decimal
from platform import python_version

import pytest
from _pytest import monkeypatch
from flask import Flask
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

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


def test_correction_rolls_back_on_event_failure(app: Flask, user: User, monkeypatch: pytest.MonkeyPatch) -> None:

    original_init = AccountBalanceEvent.__init__

    def invalid_correction_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        if self.event_type == "correction":
            self.balance_before = None

    monkeypatch.setattr(
        AccountBalanceEvent,
        "__init__",
        invalid_correction_init,
    )

    with app.app_context():

        # ARRANGE: Create an account with a valid opening event.
        account = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("5000.00"),
        )

        account_id = account.id

        # ACT: Attempt a correction with an invalid audit event.
        with pytest.raises(IntegrityError):
            correct_account_balance(
                user_id=user.id,
                account_id=account_id,
                new_balance=Decimal("1000.00"),
                reason="Simulated audit event failure",
            )

        # ASSERT: Reload the persisted account state.
        db.session.expire_all()

        saved_account = db.session.get(Account, account_id)

        assert saved_account is not None
        assert saved_account.balance == Decimal("5000.00")
        assert saved_account.user_id == user.id

        # ASSERT: Only the original opening event exists.
        events = db.session.scalars(
            select(AccountBalanceEvent).where(
                AccountBalanceEvent.account_id == account_id
            )
        ).all()

        assert len(events) == 1

        opening_event = events[0]

        assert opening_event.event_type == "opening"
        assert opening_event.amount == Decimal("5000.00")
        assert opening_event.balance_before is None
        assert opening_event.balance_after == Decimal("5000.00")

        # ASSERT: The Session is usable after rollback.
        assert db.session.is_active


def test_correct_account_balance_upward(app: Flask, user: User) -> None:
    with app.app_context():
        account = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("5000.00"),
        )

        correct_account_balance(
            user_id=user.id,
            account_id=account.id,
            new_balance=Decimal("5750.00"),
            reason="Bank reconciliation",
        )

        db.session.expire_all()
        saved_account = db.session.get(Account, account.id)

        assert saved_account is not None
        assert saved_account.balance == Decimal("5750.00")

        events = db.session.scalars(
            select(AccountBalanceEvent)
            .where(AccountBalanceEvent.account_id == account.id)
            .order_by(AccountBalanceEvent.id)
        ).all()

        assert len(events) == 2

        opening_event, correction_event = events

        # Original opening event remains unchanged.
        assert opening_event.event_type == "opening"
        assert opening_event.amount == Decimal("5000.00")
        assert opening_event.balance_before is None
        assert opening_event.balance_after == Decimal("5000.00")

        # New correction event records the increase.
        assert correction_event.event_type == "correction"
        assert correction_event.amount == Decimal("750.00")
        assert correction_event.balance_before == Decimal("5000.00")
        assert correction_event.balance_after == Decimal("5750.00")
        assert correction_event.reason == "Bank reconciliation"


@pytest.mark.parametrize(
    "incorrect_balance",
    [
        Decimal("-100.00"),   # Negative balance
        Decimal("-0.01"),     # Smallest negative cent
        Decimal("Infinity"),  # Positive infinity
        Decimal("-Infinity"), # Negative infinity
        Decimal("NaN"),       # Not a number
        Decimal("100.001"),   # More than two decimal places
    ],
)
def test_rejects_invalid_correction_balance(app: Flask, user: User, incorrect_balance: Decimal) -> None:
    with app.app_context():
        account = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("5000.00"),
        )

        account_id = account.id

        with pytest.raises(ValueError, match="Invalid new balance"):
            correct_account_balance(
                user_id=user.id,
                account_id=account_id,
                new_balance=incorrect_balance,
                reason="Invalid correction",
            )

        db.session.expire_all()
        saved_account = db.session.get(Account, account_id)

        assert saved_account is not None
        assert saved_account.balance == Decimal("5000.00")

        # The invalid request must not create an audit event.
        events = db.session.scalars(
            select(AccountBalanceEvent)
            .where(AccountBalanceEvent.account_id == account_id)
        ).all()

        assert len(events) == 1
        assert events[0].event_type == "opening"


@pytest.mark.parametrize(
    "invalid_reason",
    [
        "",
        "   ",
        None,
        123,
        "A" * 201,
    ],
)
def test_rejects_invalid_correction_reason(app: Flask, user: User, invalid_reason: str) -> None:
    with app.app_context():
        account = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("5000.00"),
        )

        account_id = account.id

        with pytest.raises(ValueError, match="Invalid correction reason"):
            correct_account_balance(
                user_id=user.id,
                account_id=account_id,
                new_balance=Decimal("4500.00"),
                reason=invalid_reason,
            )

        db.session.expire_all()
        saved_account = db.session.get(Account, account_id)

        assert saved_account is not None
        assert saved_account.balance == Decimal("5000.00")

        events = db.session.scalars(
            select(AccountBalanceEvent)
            .where(AccountBalanceEvent.account_id == account_id)
        ).all()

        assert len(events) == 1
        assert events[0].event_type == "opening"


def test_multiple_successive_corrections(app: Flask, user: User) -> None:
    with app.app_context():
        # Opening
        # Balance: 5,000 TRY
        account = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("5000.00"),
        )

        account_id = account.id

        # First correction
        # 5,000 → 4,700 TRY
        # Adjustment: −300 TRY
        correct_account_balance(
            user_id=user.id,
            account_id=account_id,
            new_balance=Decimal("4700.00"),
            reason="Bank reconciliation",
        )

        db.session.expire_all()
        saved_account = db.session.get(Account, account_id)

        assert saved_account is not None
        assert saved_account.balance == Decimal("4700.00")

        # Second correction
        # 4,700 → 5,250 TRY
        # Adjustment: +550 TRY
        correct_account_balance(
            user_id=user.id,
            account_id=account_id,
            new_balance=Decimal("5250.00"),
            reason="Bank reconciliation",

        )

        db.session.expire_all()
        saved_account = db.session.get(Account, account_id)

        assert saved_account is not None
        assert saved_account.balance == Decimal("5250.00")

        events = db.session.scalars(
            select(AccountBalanceEvent)
            .where(AccountBalanceEvent.account_id == account_id)
            .order_by(AccountBalanceEvent.id.asc())
        ).all()

        assert len(events) == 3
        assert events[0].event_type == "opening"
        assert events[1].event_type == "correction"
        assert events[2].event_type == "correction"

        opening_event, first_correction, second_correction = events

        # Opening event
        assert opening_event.event_type == "opening"
        assert opening_event.amount == Decimal("5000.00")
        assert opening_event.balance_before is None
        assert opening_event.balance_after == Decimal("5000.00")

        # First correction: 5000 -> 4700
        assert first_correction.event_type == "correction"
        assert first_correction.amount == Decimal("-300.00")
        assert first_correction.balance_before == Decimal("5000.00")
        assert first_correction.balance_after == Decimal("4700.00")

        # Second correction: 4700 -> 5250
        assert second_correction.event_type == "correction"
        assert second_correction.amount == Decimal("550.00")
        assert second_correction.balance_before == Decimal("4700.00")
        assert second_correction.balance_after == Decimal("5250.00")
