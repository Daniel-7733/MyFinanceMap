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
    return value in ['checking', 'savings']


def currency_validator(value: str) -> bool:
    """Accept supported uppercase ISO-style currency codes."""
    return value in CURRENCY_LIST


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
