"""
Module containing the Settings class for managing application settings.

The class provides attributes for specifying settings such as BOT_TOKEN,
IS_PROD, BASE_URL, etc., which can be accessed using an instance of the class
after initialization.

Example:
    SETTINGS = Settings()
    bot_token = SETTINGS.BOT_TOKEN
"""

from enum import Enum

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings


class Environment(Enum):
    TESTING = "TESTING"
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"


class DatabaseSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str


db_settings = DatabaseSettings()


class Settings(BaseSettings):
    """
    Class for managing application settings.

    This class inherits from BaseSettings and defines attributes for various
    application settings. If no default value is specified, the variable is
    looked up in the .env file (in the environment).

    These settings can be accessed using an instance.
    """

    ENVIRONMENT: Environment
    BOT_TOKEN: str
    SUPERUSER_ID: int

    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = 0
    WEBHOOK_HOST: str = ""
    WEBHOOK_PATH: str = ""
    WEBHOOK_SECRET: str = ""

    # only for self-signed
    WEBHOOK_SSL_CERT: str = ""
    WEBHOOK_SSL_PRIV: str = ""

    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int

    sql_dsn: str = (
        f"postgresql+asyncpg://{db_settings.POSTGRES_USER}:{db_settings.POSTGRES_PASSWORD}"
        f"@{db_settings.POSTGRES_HOST}:{db_settings.POSTGRES_PORT}/{db_settings.POSTGRES_DB}"
    )

    @field_validator(
        "WEBHOOK_HOST",
        "WEBHOOK_PATH",
        "WEBHOOK_SECRET",
        "WEB_SERVER_PORT",
        "WEBHOOK_SSL_CERT",
        "WEBHOOK_SSL_PRIV",
        mode="after",
    )
    @classmethod
    def webhook_fields(cls, value: str, info: ValidationInfo) -> str:
        environment = info.data.get("ENVIRONMENT", None)
        if environment and environment.value == "PRODUCTION" and not value:
            raise ValueError("field is required if ENVIRONMENT == PRODUCTION")
        return value


SETTINGS = Settings()
"""Singleton instance for managing application settings."""
