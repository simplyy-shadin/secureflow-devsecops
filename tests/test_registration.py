import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.db.models import User
from app.main import app
from app.security.password import verify_password

test_engine = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


def override_get_db():
    with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


def test_register_user_stores_hash_and_returns_safe_response() -> None:
    password = "Correct-Horse-Battery-Staple-42"

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

    with TestingSessionLocal() as session:
        user = session.scalar(
            select(User).where(User.email == "alice@secureflow.dev")
        )

        assert user is not None
        assert user.password_hash != password
        assert password not in user.password_hash
        assert verify_password(password, user.password_hash) is True


def test_register_user_rejects_duplicate_normalized_email() -> None:
    first_response = client.post(
        "/auth/register",
        json={
            "email": "Alice@SecureFlow.dev",
            "password": "Correct-Horse-Battery-Staple-42",
        },
    )
    second_response = client.post(
        "/auth/register",
        json={
            "email": "alice@secureflow.dev",
            "password": "Another-Secure-Password-99",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Registration could not be completed for this email."
    }


def test_register_user_rejects_invalid_email() -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "password": "Correct-Horse-Battery-Staple-42",
        },
    )

    assert response.status_code == 422


def test_register_user_rejects_short_password() -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "alice@secureflow.dev",
            "password": "too-short",
        },
    )

    assert response.status_code == 422
