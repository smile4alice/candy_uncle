from aiogram.filters import BaseFilter
from aiogram.types import Message

from .services import InfoCommandService


class IsCommand(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return await InfoCommandService.detect_command(message.text, message.chat.id)  # type: ignore
