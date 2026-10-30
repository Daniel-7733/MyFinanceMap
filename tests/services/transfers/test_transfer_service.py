from decimal import Decimal

import pytest
from flask import Flask
from sqlalchemy import select

from app.models import User, Account, Transfer, Transaction, db
from app.services.accounts.account_service import create_account
from app.services.transfers.transfer_service import transfer_money


def test_successful_transfer_between_accounts(app: Flask, user: User) -> None:
    with app.app_context():

        # Step 1: Create two real Accounts.
        checking = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("10000.00"),
        )

        savings = create_account(
            user_id=user.id,
            account_type="savings",
            currency="TRY",
            opening_balance=Decimal("2000.00"),
        )

        checking_id = checking.id
        savings_id = savings.id

        # Step 2: Execute the transfer.
        transfer_money(
            user_id=user.id,
            from_account_id=checking_id,
            to_account_id=savings_id,
            amount=Decimal("3000.00"),
            reason="Saving Money",
        )

        # Step 3: Expire cached ORM state.
        db.session.expire_all()

        saved_checking = db.session.get(Account, checking_id)
        saved_savings = db.session.get(Account, savings_id)

        assert saved_checking is not None
        assert saved_savings is not None

        # Step 4: Verify balances.
        assert saved_checking.balance == Decimal("7000.00")
        assert saved_savings.balance == Decimal("5000.00")

        # Step 5: Verify conservation of money.
        assert (
            saved_checking.balance + saved_savings.balance
            == Decimal("12000.00")
        )

        # Step 6: Verify the transfer history.
        transfers = db.session.scalars(
            select(Transfer).where(Transfer.user_id == user.id)
        ).all()

        assert len(transfers) == 1

        saved_transfer = transfers[0]

        assert saved_transfer.from_account_id == checking_id
        assert saved_transfer.to_account_id == savings_id
        assert saved_transfer.amount == Decimal("3000.00")
        assert saved_transfer.currency == "TRY"
        assert saved_transfer.reason == "Saving Money"

        # Step 7: Transfers must not create income/expense records.
        transactions = db.session.scalars(
            select(Transaction).where(Transaction.user_id == user.id)
        ).all()

        assert len(transactions) == 0



def test_transfer_rejects_insufficient_funds(app: Flask, user: User) -> None:
    with app.app_context():
        checking = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("1000.00"),
        )

        savings = create_account(
            user_id=user.id,
            account_type="savings",
            currency="TRY",
            opening_balance=Decimal("500.00"),
        )

        # Your task:
        # 1. Attempt to transfer 1500 TRY.
        # 2. Assert that ValueError is raised.
        with pytest.raises(ValueError, match=r"^Insufficient funds\.$"):
            transfer_money(
                user.id,
                checking.id,
                savings.id,
                Decimal("1500.00")
            )
        # 3. Reload both Accounts from the database.
        db.session.expire_all()
        # 4. Verify that their balances are unchanged.
        assert checking.balance == Decimal("1000.00")
        assert savings.balance == Decimal("500.00")
        # 5. Verify that no Transfer record was created.
        transfers = db.session.scalars(
            select(Transfer).where(
                Transfer.user_id == user.id
            )
        ).all()

        assert len(transfers) == 0



def test_invalid_currency(app: Flask, user: User) -> None:
    with app.app_context():
        checking = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("5000.00"),
        )

        savings = create_account(
            user_id=user.id,
            account_type="savings",
            currency="CAD",
            opening_balance=Decimal("100.00"),
        )

        with pytest.raises(ValueError, match=r"^Currencies are different\.$"):
            transfer_money(
                user.id,
                checking.id,
                savings.id,
                Decimal("1000.00")
            )

        db.session.expire_all()

        assert checking.balance == Decimal("5000.00")
        assert savings.balance == Decimal("100.00")

        transfers = db.session.scalars(
            select(Transfer)
            .where(
                Transfer.user_id == user.id
            )
        ).all()

        assert len(transfers) == 0



def test_transfer_rejects_account_owned_by_another_user(app: Flask, user: User) -> None:
    with app.app_context():

        # Create another user.
        other_user = User(
            username="other_user",
            email="other@example.com",
            password_hash="test-hash",
            home_currency="TRY",
            location="Test",
        )

        db.session.add(other_user)
        db.session.commit()

        # Checking belongs to our original user.
        checking = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("1000.00"),
        )

        # Savings belongs to the other user.
        savings = create_account(
            user_id=other_user.id,
            account_type="savings",
            currency="TRY",
            opening_balance=Decimal("500.00"),
        )

        # Original user attempts to transfer into another user's Account.
        with pytest.raises(LookupError, match=r"^Account does not exist or does not belong to user\.$"):
            transfer_money(
                user.id,
                checking.id,
                savings.id,
                Decimal("1000.00"),
            )

        # Reload Account balances.
        db.session.expire_all()

        # Neither balance should change.
        assert checking.balance == Decimal("1000.00")
        assert savings.balance == Decimal("500.00")

        # No Transfer record should exist.
        transfers = db.session.scalars(
            select(Transfer)
        ).all()

        assert len(transfers) == 0



def test_transfer_rejects_same_account(app: Flask, user: User) -> None:
    with app.app_context():
        checking = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("1000.00"),
        )

        with pytest.raises(ValueError, match=r"^Account IDs cannot be the same$"):
            transfer_money(
                user_id=user.id,
                from_account_id=checking.id,
                to_account_id=checking.id,
                amount=Decimal("500.00"),
            )

        db.session.expire_all()

        assert checking.balance == Decimal("1000.00")

        transfers = db.session.scalars(
            select(Transfer)
            .where(
                Transfer.user_id == user.id
            )
        ).all()

        assert len(transfers) == 0



def test_beyond_maximum_limit_account_balance(app: Flask, user: User) -> None:
    with app.app_context():
        checking = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("2000.00"),
        )

        savings = create_account(
            user_id=user.id,
            account_type="savings",
            currency="TRY",
            opening_balance=Decimal("9999999000.00"),
        )

        with pytest.raises(ValueError, match=r"^Destination balance exceeds the maximum\.$"):
            transfer_money(
                user_id=user.id,
                from_account_id=checking.id,
                to_account_id=savings.id,
                amount=Decimal("2000.00"),
            )

        db.session.expire_all()
        assert checking.balance == Decimal("2000.00")
        assert savings.balance == Decimal("9999999000.00")

        transfers = db.session.scalars(
            select(Transfer)
            .where(
                Transfer.user_id == user.id
            )
        ).all()

        assert len(transfers) == 0


def test_transfer_allows_exact_maximum_destination_balance(app: Flask, user: User) -> None:
    with app.app_context():
        checking = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("1000.00"),
        )

        savings = create_account(
            user_id=user.id,
            account_type="savings",
            currency="TRY",
            opening_balance=Decimal("9999999000.00"),
        )

        transfer_money(
            user_id=user.id,
            from_account_id=checking.id,
            to_account_id=savings.id,
            amount=Decimal("999.99"),
        )

        db.session.expire_all()

        assert checking.balance == Decimal("0.01")
        assert savings.balance == Decimal("9999999999.99")


        transfers = db.session.scalars(
            select(Transfer)
            .where(
                Transfer.user_id == user.id
            )
        ).all()

        assert len(transfers) == 1

        saved_transfer = transfers[0]

        assert saved_transfer.from_account_id == checking.id
        assert saved_transfer.to_account_id == savings.id
        assert saved_transfer.amount == Decimal("999.99")
        assert saved_transfer.currency == "TRY"

