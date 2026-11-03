from decimal import Decimal
from app.models import Transfer, db, Account
from sqlalchemy import select, update
from app.services.accounts.account_service import (
    integer_validator, string_validator, decimal_validator, MAX_ACCOUNT_BALANCE,
)


def transfer_money(user_id: int, from_account_id: int,
                   to_account_id: int, amount: Decimal, reason: str | None = None) -> Transfer:
    # Step 1: Validate identifiers.
    if not integer_validator(user_id):
        raise ValueError("Invalid user ID")

    if not integer_validator(from_account_id):
        raise ValueError("Invalid from account ID")

    if not integer_validator(to_account_id):
        raise ValueError("Invalid to account ID")

    # Step 2: Validate transfer amount.
    if not decimal_validator(amount) or amount <= 0:
        raise ValueError("Invalid transfer amount")

    # Step 3: Validate optional reason.
    if (reason is not None) and (not string_validator(reason, 200)):
        raise ValueError("Invalid reason")

    # Step 4: Verify both Accounts and ownership.
    if from_account_id == to_account_id:
        raise ValueError("Account IDs cannot be the same")

    from_account = get_owned_account(user_id, from_account_id)
    to_account = get_owned_account(user_id, to_account_id)

    if from_account is None or to_account is None:
        raise LookupError("Account does not exist or does not belong to user.")

    # Step 5: Validate transfer rules.
    # Both Accounts must use the same currency.
    if not is_same_currency(from_account, to_account):
        raise ValueError("Currencies are different.")

    # Step 6: Execute the transfer atomically.
    try:
        # Update both Account balances.
        result = db.session.execute(
            update(Account)
            .where(
                Account.id == from_account_id,
                Account.user_id == user_id,
                Account.balance >= amount,
            )
            .values(
                balance=Account.balance - amount
            )
        )

        if result.rowcount != 1:
            raise ValueError("Insufficient funds.")

        # Credit the destination Account only if its balance
        # will remain within the maximum supported limit.
        second_result = db.session.execute(
            update(Account)
            .where(
                Account.id == to_account_id,
                Account.user_id == user_id,
                Account.balance <= MAX_ACCOUNT_BALANCE - amount,
            )
            .values(
                balance=Account.balance + amount
            )
        )

        if second_result.rowcount != 1:
            raise ValueError("Destination balance exceeds the maximum.")

        # Create the historical transfer record.
        transfer = Transfer(
            user_id=user_id,
            from_account_id=from_account.id,
            to_account_id=to_account.id,
            amount=amount,
            currency=from_account.currency,
            reason=reason.strip() if reason is not None else None,
        )

        db.session.add(transfer)

        # Persist all changes together.
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return transfer


# ------------------- Helper functions ------------------- #
def get_owned_account(user_id: int, account_id: int) -> Account | None:
    """Return an Account only when it belongs to the given user."""
    return db.session.scalar(
        select(Account).where(
            Account.id == account_id,
            Account.user_id == user_id,
        )
    )

def is_same_currency(from_account: Account, to_account: Account) -> bool:
    return from_account.currency == to_account.currency
