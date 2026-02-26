from secrets import token_hex

def generate_random_string(n_bytes: int = 32) -> str:
    """
    Generate a cryptographically strong random hex string.

    NOTE: token_hex(n_bytes) returns a string of length 2 * n_bytes characters.
    Example: n_bytes=32 -> 64 hex characters.
    """
    return token_hex(n_bytes)