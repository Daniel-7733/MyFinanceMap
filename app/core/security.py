from secrets import token_hex
from werkzeug.security import generate_password_hash, check_password_hash


def generate_random_string(n_bytes: int = 32) -> str:
    """
    Generate a cryptographically strong random hex string.

    NOTE: token_hex(n_bytes) returns a string of length 2 * n_bytes characters.
    Example: n_bytes=32 -> 64 hex characters.
    """
    return token_hex(n_bytes)


def hash_password(password: str) -> str:
    """
    Hash a password.
    :param password: The Plain password.
    :return: The Hashed password.
    """
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password.
    :param password: The plain password.
    :param password_hash: The Hashed password.
    :return: Boolean representing whether the password is correct.
    """
    return check_password_hash(password_hash, password)

