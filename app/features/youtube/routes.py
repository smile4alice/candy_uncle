"""YouTube routes."""

from aiogram import F, Router
from aiogram.types import Message

from app.common.utils import error_handler
from app.features.youtube.filters import IsYouTube
from app.features.youtube.services import YouTubeService


router = Router()


# YOUTUBE DOWNLOAD VIDEO/AUDIO/SHORTS
@router.message(F.text, IsYouTube())
@error_handler
async def process_youtube_download(message: Message):
    """Process YouTube video/audio/shorts download."""
    service = YouTubeService(message)
    await service.process_youtube_content()
