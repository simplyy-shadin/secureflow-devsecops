from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SecureFlow API"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./secureflow.db"

    jwt_secret_key: SecretStr | None = Field(default=None, min_length=32)
    jwt_secret_key_file: Path | None = None
    jwt_issuer: str = "secureflow"
    jwt_audience: str = "secureflow-api"
    access_token_expire_minutes: int = Field(default=15, ge=5, le=60)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_jwt_secret_source(self) -> Self:
        source_count = int(self.jwt_secret_key is not None) + int(
            self.jwt_secret_key_file is not None
        )
        if source_count != 1:
            raise ValueError(
                "Configure exactly one of JWT_SECRET_KEY or JWT_SECRET_KEY_FILE."
            )
        return self

    def get_jwt_signing_key(self) -> str:
        if self.jwt_secret_key is not None:
            return self.jwt_secret_key.get_secret_value()

        if self.jwt_secret_key_file is None:
            raise RuntimeError("JWT signing-key source is not configured.")

        try:
            signing_key = self.jwt_secret_key_file.read_text(
                encoding="utf-8"
            ).strip()
        except OSError as exc:
            raise RuntimeError("Unable to read JWT signing-key file.") from exc

        if len(signing_key) < 32:
            raise RuntimeError(
                "JWT signing-key file must contain at least 32 characters."
            )

        return signing_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
