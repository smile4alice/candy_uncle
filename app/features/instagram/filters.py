"""Instagram filters."""

from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.features.instagram.services import InstagramService


class IsInstagram(BaseFilter):
    async def __call__(self, message: Message) -> Any:
        serv = InstagramService(message)
        result = serv._get_shortcode(message.text)
        return bool(result)
