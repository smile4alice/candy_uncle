from urllib.parse import urlparse

from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsInstagram(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False

        try:
            parsed_url = urlparse(message.text)
            return any(
                domain in parsed_url.netloc
                for domain in ["instagram.com", "www.instagram.com"]
            )
        except Exception:
            return False
