from decimal import Decimal
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