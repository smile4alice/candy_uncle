from aiogram.filters import BaseFilter
from aiogram.types import Message

from src.services.base_commands import CommandService


class IsCommand(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text.startswith("/"):  # type: ignore
            return False
        else:
            return await CommandService.detect_command(message.text)  # type: ignore
