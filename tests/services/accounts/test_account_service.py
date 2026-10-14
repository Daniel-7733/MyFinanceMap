from decimal import Decimal
from sqlalchemy.exc import IntegrityError

import pytest
from flask import Flask
from sqlalchemy import select, func
from app.models import Account, AccountBalanceEvent, Transaction, User, db
from app.services.accounts.account_service import create_account


def test_create_account_with_zero_balance(app: Flask, user: User) -> None:
    with app.app_context():

        # ACT: Ask the service to create the account.
        account = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("0.00"),
        )

        # ASSERT: The Account exists in the database.
        saved_account = db.session.get(Account, account.id)

        assert saved_account is not None
        assert saved_account.balance == Decimal("0.00")
        assert saved_account.account_type == "checking"
        assert saved_account.currency == "TRY"
        assert saved_account.user_id == user.id

        # ASSERT: Exactly one opening event exists.
        events = db.session.scalars(
            select(AccountBalanceEvent).where(
                AccountBalanceEvent.account_id == account.id
            )
        ).all()

        assert len(events) == 1

        opening_event = events[0]

        assert opening_event.event_type == "opening"
        assert opening_event.amount == Decimal("0.00")
        assert opening_event.balance_before is None
        assert opening_event.balance_after == Decimal("0.00")

        # ASSERT: Opening an account is not income or expense.
        transaction_count = db.session.scalar(
            select(func.count()).select_from(Transaction)
        )

        assert transaction_count == 0


def test_create_account_with_positive_balance(app: Flask, user: User) -> None:
    with app.app_context():
        account = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("100.00"),
        )
        saved_account = db.session.get(Account, account.id)

        assert saved_account is not None
        assert saved_account.balance == Decimal("100.00")
        assert saved_account.account_type == "checking"
        assert saved_account.currency == "TRY"
        assert saved_account.user_id == user.id

        events = db.session.scalars(
            select(AccountBalanceEvent).where(
                AccountBalanceEvent.account_id == account.id
            )
        ).all()

        assert len(events) == 1
        opening_event = events[0]

        assert opening_event.event_type == "opening"
        assert opening_event.amount == Decimal("100.00")
        assert opening_event.balance_before is None
        assert opening_event.balance_after == Decimal("100.00")

        transaction_count = db.session.scalar(
            select(func.count()).select_from(Transaction)
        )
        assert transaction_count == 0


def test_create_duplicate_account(app: Flask, user: User) -> None:
    with app.app_context():
        first_account = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("100.00"),
        )

        with pytest.raises(ValueError, match="Account already exists"):
            create_account(
                user_id=user.id,
                account_type="checking",
                currency="TRY",
                opening_balance=Decimal("100.00"),
            )

        accounts = db.session.scalars(
            select(Account).where(
                Account.user_id == user.id,
                Account.account_type == "checking",
                Account.currency == "TRY",
            )
        ).all()

        assert len(accounts) == 1
        assert accounts[0].id == first_account.id
        assert accounts[0].balance == Decimal("100.00")

        events = db.session.scalars(
            select(AccountBalanceEvent).where(
                AccountBalanceEvent.account_id == first_account.id
            )
        ).all()

        assert len(events) == 1


def test_create_account_rolls_back_on_event_failure(app: Flask, user: User, monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange: (Make the opening event invalid so SQLite rejects it)
    # -> Intercept AccountBalanceEvent creation to violate ck_balance_events_consistency
    original_init = AccountBalanceEvent.__init__

    def mock_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        if self.event_type == "opening":
            self.balance_before = Decimal("9999.99")

    monkeypatch.setattr(
        AccountBalanceEvent,
        "__init__",
        mock_init,
    )

    # ACT: The opening event should violate a CHECK constraint.
    with pytest.raises(IntegrityError):
        create_account(
            user_id=user.id,
            account_type="checking",
            currency="USD",
            opening_balance=Decimal("1000.00"),
        )

    # assert db.session.is_active

    # ASSERT: The account was not persisted.
    account_in_db = db.session.scalar(
        select(Account).where(
            Account.user_id == user.id,
            Account.account_type == "checking",
            Account.currency == "USD",
        )
    )

    assert account_in_db is None

    # ASSERT: No opening event was persisted.
    events = db.session.scalars(
        select(AccountBalanceEvent)
    ).all()

    assert events == []
