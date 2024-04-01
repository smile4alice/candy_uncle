"""
Module containing the Settings class for managing application settings.

The class provides attributes for specifying settings such as BOT_TOKEN,
IS_PROD, BASE_URL, etc., which can be accessed using an instance of the class
after initialization.

Example:
    settings = Settings()
    bot_token = settings.BOT_TOKEN
"""

import os

from pydantic_settings import BaseSettings


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

    IS_PROD: bool
    BOT_TOKEN: str
    SUPERUSER_ID: int

    BASE_URL: str
    WEBHOOK_PATH: str
    WEBHOOK_SECRET: str
    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = 5000

    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int

    # only for self-signed
    webhook_ssl_cert: str = os.path.join("static", "certs", "cert.pem")
    webhook_ssl_priv: str = os.path.join("static", "certs", "private.key")

    sql_dsn: str = (
        f"postgresql+asyncpg://{db_settings.POSTGRES_USER}:{db_settings.POSTGRES_PASSWORD}"
        f"@{db_settings.POSTGRES_HOST}:{db_settings.POSTGRES_PORT}/{db_settings.POSTGRES_DB}"
    )


SETTINGS = Settings()
"""Singleton instance for managing application settings."""
