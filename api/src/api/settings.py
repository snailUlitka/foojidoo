from functools import cache

from pydantic import PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: PostgresDsn

    access_token_expire_minutes: int
    refresh_token_expire_days: int
    token_secret_key: SecretStr
    token_algorithm: str

    @classmethod
    @field_validator("db")
    def check_db_name(cls, value: PostgresDsn) -> PostgresDsn:
        if value.path and len(value.path) > 1:
            return value

        raise ValueError

    model_config = SettingsConfigDict(
        frozen=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )


@cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[reportCallIssue]
