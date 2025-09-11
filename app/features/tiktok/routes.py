"""TikTok routes."""

from aiogram import F, Router
from aiogram.types import Message

from app.common import error_handler, TikTokAPIError
from app.features.tiktok.filters import IsTikTok
from app.features.tiktok.services import TikTokService


tiktok_router = Router()


# TIKTOK DOWNLOAD VIDEO
@tiktok_router.message(F.text, IsTikTok())
@error_handler
async def process_tiktok_download(message: Message):
    serv = TikTokService(message)
    await serv.process_tiktok_content()
