from datetime import datetime, timedelta, timezone

import jwt
from jwt import InvalidTokenError

from app.core.config import get_settings

JWT_ALGORITHM = "HS256"
_REQUIRED_CLAIMS = ["exp", "iat", "iss", "aud", "sub"]


class TokenValidationError(ValueError):
    """Raised when an access token cannot be trusted."""


def create_access_token(
    user_id: int,
    *,
    expires_delta: timedelta | None = None,
) -> str:
    if user_id <= 0:
        raise ValueError("user_id must be a positive integer")

    settings = get_settings()
    now = datetime.now(timezone.utc)
    lifetime = (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.access_token_expire_minutes)
    )
    expires_at = now + lifetime

    payload = {
        "sub": str(user_id),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.get_jwt_signing_key(),
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> int:
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.get_jwt_signing_key(),
            algorithms=[JWT_ALGORITHM],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": _REQUIRED_CLAIMS},
        )
    except InvalidTokenError as exc:
        raise TokenValidationError("Invalid access token.") from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.isdecimal():
        raise TokenValidationError("Invalid access token subject.")

    user_id = int(subject)
    if user_id <= 0:
        raise TokenValidationError("Invalid access token subject.")

    return user_id
