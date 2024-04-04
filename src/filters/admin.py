from aiogram.filters import BaseFilter
from aiogram.types import Message
from src.config import SETTINGS


class IsSuperuser(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == SETTINGS.SUPERUSER_ID  # type: ignore
