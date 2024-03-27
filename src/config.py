import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    IS_PROD: bool
    BASE_URL: str

    WEBHOOK_PATH: str
    WEBHOOK_SECRET: str
    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = 5000

    # only for self-signed
    webhook_ssl_cert: str = os.path.join("static", "certs", "cert.pem")
    webhook_ssl_priv: str = os.path.join("static", "certs", "private.key")


settings = Settings()
