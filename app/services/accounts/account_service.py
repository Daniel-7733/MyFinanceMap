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
from decimal import Decimal
from app.models import Account


def create_account(user_id: int, account_type: str, currency: str, opening_balance: Decimal) -> Account:
    """
    Create an account with its opening balance event.

    Both records must be committed atomically.

    Raises:
        ValueError: Invalid account information.
        IntegrityError: Database constraint violation.
    """
    # Step 1: Validate input.

    # Step 2: Verify the user exists.

    # Step 3: Create an Account object.

    # Step 4: Create its opening event.

    # Step 5: Add both objects to the session.

    # Step 6: Commit once.

    # Step 7: Return the Account.

    raise NotImplementedError