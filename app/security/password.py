from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

_password_hasher = PasswordHasher()
_dummy_password_hash = _password_hasher.hash(
    "secureflow-authentication-timing-placeholder"
)


def hash_password(password: str) -> str:
    """Hash a plaintext password with Argon2id."""
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    """Verify a password while preserving hash work for unknown users."""
    has_real_hash = password_hash is not None
    target_hash = password_hash if has_real_hash else _dummy_password_hash

    try:
        verified = _password_hasher.verify(target_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False

    return has_real_hash and verified
