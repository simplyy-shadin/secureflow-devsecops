from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SecureFlow API"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./secureflow.db"

    jwt_secret_key: SecretStr = Field(min_length=32)
    jwt_issuer: str = "secureflow"
    jwt_audience: str = "secureflow-api"
    access_token_expire_minutes: int = Field(default=15, ge=5, le=60)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
