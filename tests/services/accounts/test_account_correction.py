from decimal import Decimal
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
