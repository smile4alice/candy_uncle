from re import findall
from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsInstagram(BaseFilter):
    async def __call__(self, message: Message) -> Any:
        return findall(r"instagram.com\/.+", message.text)  # type: ignore
