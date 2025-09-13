"""TikTok routes."""

from aiogram import F, Router
from aiogram.types import Message

from app.common.utils import error_handler
from app.features.tiktok.filters import IsTikTok
from app.features.tiktok.services import TikTokService


router = Router()


# TIKTOK DOWNLOAD VIDEO
@router.message(F.text, IsTikTok())
@error_handler
async def process_tiktok_download(message: Message):
    serv = TikTokService(message)
    await serv.process_tiktok_content()
