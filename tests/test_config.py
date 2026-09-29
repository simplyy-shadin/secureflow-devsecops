import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_reads_jwt_signing_key_from_file(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    signing_key = "k" * 64
    key_file = tmp_path / "jwt-secret-key"
    key_file.write_text(f"{signing_key}\n", encoding="utf-8")

    settings = Settings(
        jwt_secret_key_file=key_file,
        _env_file=None,
    )

    assert settings.get_jwt_signing_key() == signing_key


def test_settings_rejects_multiple_jwt_secret_sources(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    key_file = tmp_path / "jwt-secret-key"
    key_file.write_text("f" * 64, encoding="utf-8")

    with pytest.raises(ValidationError):
        Settings(
            jwt_secret_key="e" * 64,
            jwt_secret_key_file=key_file,
            _env_file=None,
        )


def test_settings_rejects_missing_jwt_secret_source(monkeypatch) -> None:
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY_FILE", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_rejects_short_file_secret(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    key_file = tmp_path / "jwt-secret-key"
    key_file.write_text("too-short", encoding="utf-8")

    settings = Settings(
        jwt_secret_key_file=key_file,
        _env_file=None,
    )

    with pytest.raises(RuntimeError):
        settings.get_jwt_signing_key()
