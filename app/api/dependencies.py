from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.security.tokens import TokenValidationError, decode_access_token

DbSession = Annotated[Session, Depends(get_db)]

_bearer_scheme = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(_bearer_scheme),
]


def _authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: BearerCredentials,
    db: DbSession,
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _authentication_error()

    try:
        user_id = decode_access_token(credentials.credentials)
    except TokenValidationError as exc:
        raise _authentication_error() from exc

    user = db.get(User, user_id)
    if user is None:
        raise _authentication_error()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
