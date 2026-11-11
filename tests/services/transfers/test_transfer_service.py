import threading
from decimal import Decimal
import pytest
from flask import Flask
from sqlalchemy import select, event
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session
from app.models import User, Account, Transfer, Transaction, db
from app.services.accounts.account_service import create_account
from app.services.transfers.transfer_service import transfer_money
from threading import Thread, Barrier



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



def test_transfer_rolls_back_when_commit_fails(app: Flask, user: User, monkeypatch: pytest.MonkeyPatch) -> None:
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
            currency="TRY",
            opening_balance=Decimal("2000.00"),
        )

        checking_id = checking.id
        savings_id = savings.id

        # Your exercise starts here.
        # Simulate a failure whenever commit() is called.
        def failing_commit() -> None:
            raise RuntimeError("Simulated commit failure")

        # Replace the real commit method temporarily.
        with monkeypatch.context() as patch:
            patch.setattr(db.session, "commit", failing_commit)

            # The transfer should fail during commit.
            with pytest.raises(RuntimeError, match=r"^Simulated commit failure$"):
                transfer_money(
                    user_id=user.id,
                    from_account_id=checking_id,
                    to_account_id=savings_id,
                    amount=Decimal("500.00"),
                )

        # Reload the persisted Account state.
        db.session.expire_all()

        saved_checking = db.session.get(Account, checking_id)
        saved_savings = db.session.get(Account, savings_id)

        assert saved_checking is not None
        assert saved_savings is not None

        assert saved_checking.balance == Decimal("5000.00")
        assert saved_savings.balance == Decimal("2000.00")

        # No Transfer record should have been persisted.
        transfers = db.session.scalars(
            select(Transfer).where(
                Transfer.user_id == user.id
            )
        ).all()

        assert len(transfers) == 0



def test_transfer_rolls_back_on_database_constraint_failure(app: Flask, user: User) -> None:
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
            currency="TRY",
            opening_balance=Decimal("2000.00"),
        )

        checking_id = checking.id
        savings_id = savings.id

        # This listener deliberately corrupts the Transfer amount
        # immediately before SQLAlchemy generates the INSERT.
        def force_invalid_amount(mapper, connection, target):
            target.amount = Decimal("-1000.00")

        event.listen(Transfer, "before_insert", force_invalid_amount)

        try:
            with pytest.raises(IntegrityError):
                transfer_money(
                    user_id=user.id,
                    from_account_id=checking_id,
                    to_account_id=savings_id,
                    amount=Decimal("1000.00"),
                )
        finally:
            # Always remove the listener, even if the test fails.
            event.remove(Transfer, "before_insert", force_invalid_amount)

        db.session.expire_all()

        saved_checking = db.session.get(Account, checking_id)
        saved_savings = db.session.get(Account, savings_id)

        assert saved_checking is not None
        assert saved_savings is not None

        assert saved_checking.balance == Decimal("5000.00")
        assert saved_savings.balance == Decimal("2000.00")

        transfers = db.session.scalars(
            select(Transfer)
            .where(
                Transfer.user_id == user.id
            )
        ).all()

        assert len(transfers) == 0



def test_transfer_rolls_back_when_destination_exceeds_limit(app: Flask, user: User) -> None:
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
            currency="TRY",
            opening_balance=Decimal("9999999500.00"),
        )

        with pytest.raises(ValueError, match=r"^Destination balance exceeds the maximum\.$"):
            transfer_money(
                user_id=user.id,
                from_account_id=checking.id,
                to_account_id=savings.id,
                amount=Decimal("1000.00"),
            )

        db.session.expire_all()

        assert checking.balance == Decimal("5000.00")
        assert savings.balance == Decimal("9999999500.00")

        transfers = db.session.scalars(
            select(Transfer)
            .where(
                Transfer.user_id == user.id
            )
        ).all()

        assert len(transfers) == 0



def test_two_transfers_cannot_overspend_same_source(app: Flask, user: User) -> None:

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
            currency="TRY",
            opening_balance=Decimal("0.00"),
        )

        transfer_money(
            user_id=user.id,
            from_account_id=checking.id,
            to_account_id=savings.id,
            amount=Decimal("4000.00"),
        )


        with pytest.raises(ValueError, match=r"^Insufficient funds\.$"):
            transfer_money(
                user_id=user.id,
                from_account_id=checking.id,
                to_account_id=savings.id,
                amount=Decimal("3000.00"),
            )

        db.session.expire_all()
        assert checking.balance == Decimal("1000.00")
        assert savings.balance == Decimal("4000.00")

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
        assert saved_transfer.amount == Decimal("4000.00")
        assert saved_transfer.currency == "TRY"



def test_two_threads_can_read_same_account(app: Flask, user: User) -> None:
    with app.app_context():
        checking = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("5000.00"),
        )

        account_id = checking.id

    barrier = Barrier(2)

    results: dict[str, Decimal] = {}
    errors: list[Exception] = []

    def worker(name: str) -> None:
        try:
            with app.app_context():
                barrier.wait(timeout=5)

                account = db.session.get(Account, account_id)

                if account is None:
                    raise LookupError("Account not found")

                results[name] = account.balance

        except Exception as exc:
            errors.append(exc)

    # Create thread_a and thread_b.
    thread_a = Thread(target=worker, args=("A",))
    thread_b = Thread(target=worker, args=("B",))
    # Start both.
    thread_a.start()
    thread_b.start()
    # Join both.
    thread_a.join(timeout=10)
    thread_b.join(timeout=10)

    assert not thread_a.is_alive()
    assert not thread_b.is_alive()

    assert len(results) == 2

    # Verify results and errors.
    assert not errors
    assert results == {
        "A": Decimal("5000.00"),
        "B": Decimal("5000.00"),
    }



def test_concurrent_database_setup(concurrent_app: Flask) -> None:
    with concurrent_app.app_context():
        assert db.engine.url.database is not None
        assert db.engine.url.database.endswith("concurrency.db")





def test_concurrent_transfers_cannot_overspend(concurrent_app: Flask) -> None:
    """
    Test that two concurrent transfers cannot overspend one account.

    Initial balances:
        Checking: 5000 TRY
        Savings:     0 TRY

    Concurrent requests:
        Thread A: Transfer 2000 TRY
        Thread B: Transfer 4000 TRY

    Financial invariants:
        1. Neither account becomes negative.
        2. Total money remains 5000 TRY.
        3. Both transfers cannot succeed.
        4. Successful transfers match database balances.
        5. Transfer history matches committed transfers.
    """

    # --------------------------------------------------
    # STEP 1: Prepare the test database
    # --------------------------------------------------

    with concurrent_app.app_context():
        test_user = User(
            username="test_user",
            email="test_user@example.com",
            password_hash="test-hash",
            home_currency="TRY",
            location="Test",
        )

        db.session.add(test_user)
        db.session.commit()

        checking = create_account(
            user_id=test_user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("5000.00"),
        )

        savings = create_account(
            user_id=test_user.id,
            account_type="savings",
            currency="TRY",
            opening_balance=Decimal("0.00"),
        )

        # Save plain IDs rather than sharing ORM objects
        # between different thread Sessions.
        user_id = test_user.id
        checking_id = checking.id
        savings_id = savings.id

        # Ensure account setup is committed before workers run.
        db.session.commit()

    # --------------------------------------------------
    # STEP 2: Prepare synchronization and results
    # --------------------------------------------------

    barrier = Barrier(2)

    # Successful transfers are recorded here.
    results: dict[str, Decimal] = {}

    # Failed transfers are recorded here.
    errors: dict[str, Exception] = {}

    # --------------------------------------------------
    # STEP 3: Define the worker
    # --------------------------------------------------

    def worker(name: str, amount: Decimal) -> None:
        try:
            # Each worker needs its own Flask application context.
            with concurrent_app.app_context():

                # Wait until both threads are ready.
                barrier.wait(timeout=5)

                # Attempt the transfer.
                transfer_money(
                    user_id=user_id,
                    from_account_id=checking_id,
                    to_account_id=savings_id,
                    amount=amount,
                )

                # Record success only after transfer_money returns.
                # This assumes the service commits before returning.
                results[name] = amount

        except Exception as exc:
            errors[name] = exc

    # --------------------------------------------------
    # STEP 4: Create and start both threads
    # --------------------------------------------------

    thread_a = Thread(
        target=worker,
        args=("A", Decimal("2000.00")),
    )

    thread_b = Thread(
        target=worker,
        args=("B", Decimal("4000.00")),
    )

    thread_a.start()
    thread_b.start()

    # Wait for both threads to finish.
    thread_a.join(timeout=10)
    thread_b.join(timeout=10)

    assert not thread_a.is_alive(), "Thread A did not finish."
    assert not thread_b.is_alive(), "Thread B did not finish."

    # --------------------------------------------------
    # STEP 5: Inspect worker outcomes
    # --------------------------------------------------

    print("\n--- Concurrent Transfer Results ---")
    print("Successful transfers:", results)

    for name, error in errors.items():
        print(f"Thread {name} failed: {type(error).__name__}: {error}")

    # Only expected business rejections or SQLite lock errors
    # are acceptable outcomes for this experiment.
    for name, error in errors.items():
        if isinstance(error, ValueError):
            assert str(error) == "Insufficient funds.", (
                f"Unexpected business rejection in thread {name}: {error}"
            )

        elif isinstance(error, OperationalError):
            # SQLite can report lock contention during
            # concurrent writes. Keep this visible.
            assert "locked" in str(error).lower(), (
                f"Unexpected database error in thread {name}: {error}"
            )

        else:
            pytest.fail(
                f"Unexpected exception in thread {name}: "
                f"{type(error).__name__}: {error}"
            )

    # Every worker must have exactly one recorded outcome.
    assert len(results) + len(errors) == 2

    # Both transfers total 6000 TRY, exceeding the available 5000.
    assert not ("A" in results and "B" in results), (
        "Critical failure: Both transfers succeeded!"
    )

    # --------------------------------------------------
    # STEP 6: Reload the committed database state
    # --------------------------------------------------

    with concurrent_app.app_context():
        db_checking = db.session.get(Account, checking_id)
        db_savings = db.session.get(Account, savings_id)

        assert db_checking is not None
        assert db_savings is not None

        # INVARIANT 1: No negative balances.
        assert db_checking.balance >= Decimal("0.00")
        assert db_savings.balance >= Decimal("0.00")

        # INVARIANT 2: Money must be conserved.
        total_balance = db_checking.balance + db_savings.balance

        assert total_balance == Decimal("5000.00"), (
            f"Money conservation failed: {total_balance}"
        )

        # INVARIANT 3: Balances match successful transfers.
        successful_amount = sum(
            results.values(),
            Decimal("0.00"),
        )

        assert db_checking.balance == (
            Decimal("5000.00") - successful_amount
        )

        assert db_savings.balance == successful_amount

        # --------------------------------------------------
        # STEP 7: Verify Transfer history
        # --------------------------------------------------

        transfers = db.session.scalars(
            select(Transfer).where(
                Transfer.user_id == user_id
            )
        ).all()

        # INVARIANT 4: Each successful transfer has one record.
        assert len(transfers) == len(results)

        # INVARIANT 5: Recorded amounts match successful requests.
        assert sorted(
            transfer.amount for transfer in transfers
        ) == sorted(results.values())

        # INVARIANT 6: Every record references the correct accounts.
        for transfer in transfers:
            assert transfer.from_account_id == checking_id
            assert transfer.to_account_id == savings_id
            assert transfer.currency == "TRY"

        print("\n--- Final Database State ---")
        print("Checking:", db_checking.balance)
        print("Savings:", db_savings.balance)
        print("Transfer records:", len(transfers))

    # --------------------------------------------------
    # STEP 8: Verify a transfer actually succeeded
    # --------------------------------------------------

    # We want to demonstrate successful financial processing,
    # not merely that both requests encountered database errors.
    assert len(results) == 1, (
        f"Expected one successful transfer, got {len(results)}. "
        f"Errors: {errors}"
    )




def test_account_balance_remains_stale_until_refreshed(concurrent_app: Flask) -> None:
    with concurrent_app.app_context():
        user = User(
            username="user",
            email="user@example.com",
            password_hash="test-hash",
            home_currency="TRY",
            location="Test",
        )

        db.session.add(user)
        db.session.commit()

        checking = create_account(
            user_id=user.id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("5000.00"),
        )

        checking_id = checking.id

        # Create two independent sessions.
        # Load Checking into account_a using session_a and into account_b using session_b.
        with Session(db.engine) as session_a, Session(db.engine) as session_b:
            account_a = session_a.get(Account, checking_id)
            account_b = session_b.get(Account, checking_id)

            # Set account_a.balance to 3000 and commit session_a.
            account_a.balance = Decimal("3000.00")
            session_a.commit()

            # Check B's existing object
            assert account_b.balance == Decimal("5000.00")

            # Ask B's session to reload its object
            session_b.refresh(account_b)

            # Check the reloaded object
            assert account_b.balance == Decimal("3000.00")



def test_competing_transfers_after_both_read_same_balance(concurrent_app: Flask) -> None:
    with concurrent_app.app_context():
        user = User(
            username="user",
            email="user@example.com",
            password_hash="test-hash",
            home_currency="TRY",
            location="Test",
        )

        db.session.add(user)
        db.session.commit()
        user_id = user.id

        checking = create_account(
            user_id=user_id,
            account_type="checking",
            currency="TRY",
            opening_balance=Decimal("5000.00"),
        )

        savings = create_account(
            user_id=user_id,
            account_type="savings",
            currency="TRY",
            opening_balance=Decimal("0.00"),
        )

        checking_id = checking.id
        savings_id = savings.id

    barrier = Barrier(2)

    balances_read: dict[str, Decimal] = {}
    results: dict[str, Decimal] = {}
    errors: list[Exception] = []

    def worker(name: str, amount: Decimal) -> None:
        try:
            with concurrent_app.app_context():
                account = db.session.get(Account, checking_id)

                if account is None:
                    raise LookupError("Account not found")

                balances_read[name] = account.balance

                # Neither worker proceeds until both have read the balance.
                barrier.wait(timeout=5)

                transfer_money(
                    user_id=user_id,
                    from_account_id=checking_id,
                    to_account_id=savings_id,
                    amount=amount,
                )
                results[name] = amount

        except Exception as exc:
            errors.append(exc)

    thread_a = Thread(
        target=worker,
        args=("Thread_A", Decimal("2000.00")),
    )
    thread_b = Thread(
        target=worker,
        args=("Thread_B", Decimal("4000.00")),
    )

    thread_a.start()
    thread_b.start()

    thread_a.join(timeout=10)
    thread_b.join(timeout=10)

    assert not thread_a.is_alive()
    assert not thread_b.is_alive()

    # Both workers read the original balance before attempting transfers.
    assert balances_read == {
        "Thread_A": Decimal("5000.00"),
        "Thread_B": Decimal("5000.00"),
    }

    # Exactly one transfer should succeed; we do not choose which one.
    assert len(results) == 1
    assert len(errors) == 1
    assert isinstance(errors[0], ValueError)
    assert str(errors[0]) == "Insufficient funds."



