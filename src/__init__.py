from aiogram import Bot

from .config import settings


BOT = Bot(token=settings.BOT_TOKEN)
print(123123)
__all__ = (
    "settings",
    "BOT",
)
