from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

MIN_SECRET_LENGTH = 32


class Settings(BaseSettings):
    """All app configuration, read from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    # App
    app_env: Literal["development", "test", "production"] = "development"
    port: int = Field(default=8000, ge=1, le=65535)

    # Database
    database_url: str = Field(min_length=1)

    # Auth
    jwt_access_secret: SecretStr
    jwt_refresh_secret: SecretStr
    access_token_expires_minutes: int = Field(default=15, ge=1, le=60)
    refresh_token_expires_days: int = Field(default=7, ge=1, le=30)

    # Optional until later phases
    openai_api_key: SecretStr | None = None
    redis_url: str | None = None

    @field_validator("jwt_access_secret", "jwt_refresh_secret")
    @classmethod
    def secret_long_enough(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < MIN_SECRET_LENGTH:
            raise ValueError(f"must be at least {MIN_SECRET_LENGTH} characters")
        return value

    @model_validator(mode="after")
    def secrets_must_differ(self) -> "Settings":
        if self.jwt_access_secret.get_secret_value() == self.jwt_refresh_secret.get_secret_value():
            raise ValueError("JWT_ACCESS_SECRET and JWT_REFRESH_SECRET must be different")
        return self

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


def _load_settings() -> Settings:
    """Build settings, or stop the app with a readable list of problems."""
    try:
        return Settings()
    except ValidationError as exc:
        lines = ["Invalid configuration. Fix these values in your .env file:"]
        for error in exc.errors():
            field = ".".join(str(part) for part in error["loc"]).upper() or "SETTINGS"
            lines.append(f"  - {field}: {error['msg']}")
        raise SystemExit("\n".join(lines)) from None


@lru_cache
def get_settings() -> Settings:
    """Return the one shared Settings object (created on first call)."""
    return _load_settings()