from decimal import Decimal
from app.models import Transfer


def transfer_money(user_id: int, from_account_id: int, to_account_id: int, amount: Decimal, reason: str | None = None) -> Transfer:
    raise NotImplementedError