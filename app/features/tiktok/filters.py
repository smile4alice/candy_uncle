"""TikTok filters."""

from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.features.tiktok.services import TikTokService


class IsTikTok(BaseFilter):
    async def __call__(self, message: Message) -> Any:
        serv = TikTokService(message)
        result = serv._get_video_id(message.text)
        return bool(result)
