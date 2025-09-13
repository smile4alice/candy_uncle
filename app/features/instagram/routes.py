"""Instagram routes."""

from aiogram import F, Router
from aiogram.types import Message

from app.common.utils import error_handler
from app.features.instagram.filters import IsInstagram
from app.features.instagram.services import InstagramService


router = Router()


# INSTAGRAM DOWNLOAD VIDEO
@router.message(F.text, IsInstagram())
@error_handler
async def process_instagram_download(message: Message):
    serv = InstagramService(message)
    await serv.process_instagram_content()
