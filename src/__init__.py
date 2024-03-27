from aiogram import Bot
from .config import settings

BOT = Bot(token=settings.BOT_TOKEN)

__all__ = (
    "settings",
    "BOT",
)
