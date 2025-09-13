"""YouTube filters."""

import re
from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsYouTube(BaseFilter):
    """Filter for YouTube URLs."""

    async def __call__(self, message: Message, **kwargs: Any) -> bool:
        """
        Check if message contains YouTube URL.

        :param message: Telegram message
        :return: True if message contains YouTube URL
        """
        if not message.text:
            return False

        # YouTube URL patterns - only videos, shorts, and music
        patterns = [
            r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
        ]

        for pattern in patterns:
            if re.search(pattern, message.text):
                return True

        return False
