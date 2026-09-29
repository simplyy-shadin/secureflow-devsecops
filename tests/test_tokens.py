from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import get_settings
from app.security.tokens import (
    JWT_ALGORITHM,
    TokenValidationError,
    create_access_token,
    decode_access_token,
)


def test_access_token_round_trip_returns_user_id() -> None:
    token = create_access_token(42)

    assert decode_access_token(token) == 42


def test_expired_access_token_is_rejected() -> None:
    token = create_access_token(42, expires_delta=timedelta(seconds=-1))

    with pytest.raises(TokenValidationError):
        decode_access_token(token)


def test_tampered_access_token_is_rejected() -> None:
    token = create_access_token(42)
    header, payload, signature = token.split(".")

    index = len(signature) // 2
    replacement = "a" if signature[index] != "a" else "b"
    tampered_signature = (
        f"{signature[:index]}{replacement}{signature[index + 1:]}"
    )
    tampered_token = f"{header}.{payload}.{tampered_signature}"

    with pytest.raises(TokenValidationError):
        decode_access_token(tampered_token)


def test_access_token_with_wrong_audience_is_rejected() -> None:
    settings = get_settings()
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "42",
            "iss": settings.jwt_issuer,
            "aud": "another-api",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(TokenValidationError):
        decode_access_token(token)
