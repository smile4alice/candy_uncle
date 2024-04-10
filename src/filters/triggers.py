from aiogram.filters import BaseFilter
from aiogram.types import Message

from src.services.triggers import TriggerService


class IsTrigger(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return await TriggerService.detect_triggers(
            message.text,  # type: ignore
            chat_id=message.chat.id,
        )
