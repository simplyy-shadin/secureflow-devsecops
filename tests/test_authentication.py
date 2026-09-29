from datetime import timedelta

from app.security.tokens import create_access_token

_TEST_EMAIL = "alice@secureflow.dev"
_TEST_PASSWORD = "Correct-Horse-Battery-Staple-42"


def register_test_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": _TEST_EMAIL,
            "password": _TEST_PASSWORD,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_login_returns_bearer_token_and_allows_profile_access(client) -> None:
    registered_user = register_test_user(client)

    login_response = client.post(
        "/auth/login",
        json={
            "email": "  Alice@SecureFlow.dev  ",
            "password": _TEST_PASSWORD,
        },
    )

    assert login_response.status_code == 200
    token_body = login_response.json()
    assert token_body["token_type"] == "bearer"
    assert token_body["expires_in"] == 900
    assert token_body["access_token"]

    profile_response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token_body['access_token']}",
        },
    )

    assert profile_response.status_code == 200
    assert profile_response.json() == registered_user


def test_login_uses_same_error_for_wrong_password_and_unknown_user(client) -> None:
    register_test_user(client)

    wrong_password = client.post(
        "/auth/login",
        json={
            "email": _TEST_EMAIL,
            "password": "Definitely-Wrong-Password",
        },
    )
    unknown_user = client.post(
        "/auth/login",
        json={
            "email": "nobody@secureflow.dev",
            "password": "Definitely-Wrong-Password",
        },
    )

    assert wrong_password.status_code == 401
    assert unknown_user.status_code == 401
    assert wrong_password.json() == unknown_user.json()
    assert wrong_password.headers["www-authenticate"] == "Bearer"
    assert unknown_user.headers["www-authenticate"] == "Bearer"


def test_profile_requires_bearer_token(client) -> None:
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials."}
    assert response.headers["www-authenticate"] == "Bearer"


def test_profile_rejects_malformed_token(client) -> None:
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials."}


def test_profile_rejects_expired_token(client) -> None:
    registered_user = register_test_user(client)
    expired_token = create_access_token(
        registered_user["id"],
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials."}
