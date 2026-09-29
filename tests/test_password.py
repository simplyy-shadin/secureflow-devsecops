from app.security.password import hash_password, verify_password


def test_password_hash_does_not_store_plaintext() -> None:
    password = "Correct-Horse-Battery-Staple-42"

    password_hash = hash_password(password)

    assert password_hash != password
    assert password not in password_hash
    assert password_hash.startswith("$argon2id$")


def test_password_verification_accepts_correct_password() -> None:
    password = "Correct-Horse-Battery-Staple-42"
    password_hash = hash_password(password)

    assert verify_password(password, password_hash) is True


def test_password_verification_rejects_incorrect_password() -> None:
    password_hash = hash_password("Correct-Horse-Battery-Staple-42")

    assert verify_password("wrong-password", password_hash) is False


def test_password_verification_rejects_invalid_hash() -> None:
    assert verify_password("password", "not-an-argon2-hash") is False
