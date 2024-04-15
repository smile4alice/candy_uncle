from aiogram.filters import BaseFilter
from aiogram.types import Message

from src.services.info_commands import InfoCommandService


class IsCommand(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return await InfoCommandService.detect_command(message.text)  # type: ignore
