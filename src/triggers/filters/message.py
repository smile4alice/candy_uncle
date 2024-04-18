from aiogram.filters import BaseFilter
from aiogram.types import Message

from ..services import TriggerEventService


class IsTrigger(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        result = await TriggerEventService.detect_triggers(
            message.text, chat_id=message.chat.id  # type: ignore
        )
        return bool(result)
