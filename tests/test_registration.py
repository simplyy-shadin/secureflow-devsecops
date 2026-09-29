from sqlalchemy import select

from app.db.models import User
from app.security.password import verify_password
from tests.helpers import synthetic_password


def test_register_user_stores_hash_and_returns_safe_response(
    client,
    db_session_factory,
) -> None:
    password = synthetic_password()

    response = client.post(
        "/auth/register",
        json={
            "email": "  Alice@SecureFlow.dev  ",
            "password": password,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@secureflow.dev"
    assert set(body) == {"id", "email", "created_at"}

    with db_session_factory() as session:
        user = session.scalar(
            select(User).where(User.email == "alice@secureflow.dev")
        )

        assert user is not None
        assert user.password_hash != password
        assert password not in user.password_hash
        assert verify_password(password, user.password_hash) is True


def test_register_user_rejects_duplicate_normalized_email(client) -> None:
    password = synthetic_password()

    first_response = client.post(
        "/auth/register",
        json={
            "email": "Alice@SecureFlow.dev",
            "password": password,
        },
    )
    second_response = client.post(
        "/auth/register",
        json={
            "email": "alice@secureflow.dev",
            "password": f"{password}-alternate",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Registration could not be completed for this email."
    }


def test_register_user_rejects_invalid_email(client) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "password": synthetic_password(),
        },
    )

    assert response.status_code == 422


def test_register_user_rejects_short_password(client) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "alice@secureflow.dev",
            "password": "too-short",
        },
    )

    assert response.status_code == 422
