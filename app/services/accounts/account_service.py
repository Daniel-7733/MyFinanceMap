"""
Flask Route
    │
    ▼
AccountService
    │
    ├── Validate user and input
    │
    ├── Create Account
    │
    ├── Create Opening Event
    │
    └── Commit atomically
             │
             ▼
       SQLite Database
"""
from decimal import Decimal, InvalidOperation
from sqlalchemy import select
from app.models import Account, AccountBalanceEvent, db, User
from app.core.currencies import CURRENCY_LIST



MAX_ACCOUNT_BALANCE = Decimal("9999999999.99")
CENT = Decimal("0.01")


def create_account(user_id: int, account_type: str, currency: str,
                   opening_balance: Decimal) -> Account:
    """
    Create an account with its opening balance event.

    Both records must be committed atomically.

    Raises:
        ValueError: Invalid account information.
        IntegrityError: Database constraint violation.
    """
    # Step 1: Validate input.
    if not integer_validator(user_id):
        raise ValueError("Invalid user ID")
    if not account_type_validator(account_type):
        raise ValueError("Invalid account type")
    if not currency_validator(currency):
        raise ValueError("Invalid currency")
    if not decimal_validator(opening_balance):
        raise ValueError("Invalid opening balance")

    # Step 2: Verify the user exists.
    if not does_user_exist(user_id):
        raise ValueError("Invalid user ID")

    if does_account_exist(user_id, account_type, currency):
        raise ValueError("Account already exists")

    # Step 3: Create an Account object.
    account = Account(
        user_id=user_id,
        account_type=account_type,
        currency=currency,
        balance=opening_balance,
    )

    # Step 4: Create its opening event.
    event = AccountBalanceEvent(
        account=account,
        event_type="opening",
        amount=opening_balance,
        balance_before=None,
        balance_after=opening_balance,
        reason="Account initialized",
    )

    try:
        db.session.add_all([account, event])
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return account


    # --------------- The Pipeline ---------------
    #      Flask Route
    #           │
    #           ▼
    # correct_account_balance()
    #       │
    #       ├── Validate inputs
    #       │
    #       ├── Find Account belonging to user
    #       │
    #       ├── Read current balance
    #       │
    #       ├── Calculate signed difference
    #       │
    #       ├── Create correction event
    #       │
    #       ├── Update Account.balance
    #       │
    #       └── Commit both atomically
    #                  │
    #                  ▼
    #             SQLite Database
    # ---------------------------------------------
def correct_account_balance(user_id: int, account_id: int, new_balance: Decimal, reason: str) -> Account:
    """
    Correct an existing account balance.

    Update the account and create an audit event
    in one database transaction.
    """

    # Step 1: Validate inputs.
    if not integer_validator(user_id):
        raise ValueError("Invalid user ID")

    if not integer_validator(account_id):
        raise ValueError("Invalid account ID")

    if not decimal_validator(new_balance):
        raise ValueError("Invalid new balance")

    if not string_validator(reason, string_length=200):
        raise ValueError("Invalid correction reason")

    # Step 2: Find the account owned by this user.
    account = db.session.scalar(
        select(Account).where(
            Account.id == account_id,
            Account.user_id == user_id,
        )
    )

    if account is None:
        raise LookupError("Account does not exist or does not belong to user.")

    # Step 3: Read the existing balance.
    balance_before = account.balance

    # Step 4: No correction is necessary.
    if balance_before == new_balance:
        return account

    # Step 5: Calculate the signed adjustment.
    adjustment = new_balance - balance_before

    # Step 6: Create an audit event.
    event = AccountBalanceEvent(
        account=account,
        event_type="correction",
        amount=adjustment,
        balance_before=balance_before,
        balance_after=new_balance,
        reason=reason.strip(),
    )

    # Step 7: Update the existing account.
    account.balance = new_balance

    # Step 8: Persist both operations atomically.
    try:
        db.session.add(event)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    # Step 9: Return the existing account.
    return account


# ------------------- Helper functions ------------------- #
def integer_validator(number: int) -> bool:
    """
    Return True only for positive integers.
    Reject bool.
    """
    # Explicitly reject boolean types because isinstance(True, int) is True
    return type(number) is int and number > 0


def account_type_validator(value: str) -> bool:
    """Accept only 'checking' or 'savings'."""
    return isinstance(value, str) and value in (
        "checking",
        "savings",
    )


def currency_validator(value: str) -> bool:
    """Accept supported uppercase ISO-style currency codes."""
    return isinstance(value, str) and value in CURRENCY_LIST


def string_validator(value: str, string_length: int = 200) -> bool:
    """Validates if a value is a non-empty string within a specific length."""
    # 1. First, strictly verify it is a string
    if not isinstance(value, str):
        return False

    # 2. Now it is safe to check stripping and length
    if not value.strip() or len(value) > string_length:
        return False

    return True


def decimal_validator(number: Decimal) -> bool:
    """
    Accept only:
    - Decimal instances
    - finite values
    - values >= 0
    - at most two fractional decimal places
    """
    if not isinstance(number, Decimal):
        return False

    if not number.is_finite():
        return False

    if number < 0 or number > MAX_ACCOUNT_BALANCE:
        return False

    try:
        return number == number.quantize(CENT)
    except InvalidOperation:
        return False


def does_user_exist(user_id: int) -> bool:
    return db.session.get(User, user_id) is not None

def does_account_exist(user_id: int, account_type: str, currency:str) -> bool:
    existing_account = db.session.scalar(
        select(Account).where(
            Account.user_id == user_id,
            Account.account_type == account_type,
            Account.currency == currency,
        )
    )

    return existing_account is not None
