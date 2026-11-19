"""Password hashing with Argon2id (argon2-cffi defaults follow RFC 9106 guidance)."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

_hasher = PasswordHasher()

# Verified when the email is unknown, so response time does not reveal which
# emails are registered (user enumeration via timing).
_DUMMY_HASH = _hasher.hash("timing-equalizer-not-a-real-password")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    """False for wrong passwords AND for unusable hashes (e.g. demo accounts)."""
    if not password_hash:
        _burn_time(password)
        return False
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(password_hash: str) -> bool:
    try:
        return _hasher.check_needs_rehash(password_hash)
    except InvalidHashError:
        return False


def _burn_time(password: str) -> None:
    try:
        _hasher.verify(_DUMMY_HASH, password)
    except VerifyMismatchError:
        pass


def verify_unknown_user(password: str) -> None:
    """Spend the same time as a real check when no user matches the email."""
    _burn_time(password)
