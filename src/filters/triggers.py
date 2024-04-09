from aiogram.filters import BaseFilter
from aiogram.types import Message

from src.services.triggers import TriggersService


class IsTrigger(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return await TriggersService.detect_trigger(
            message.text,  # type: ignore
            chat_id=message.chat.id,
        )
