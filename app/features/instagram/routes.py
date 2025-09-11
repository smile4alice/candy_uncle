"""Instagram routes."""

from aiogram import F, Router
from aiogram.types import Message

from app.common import error_handler, InstagramAPIError
from app.features.instagram.filters import IsInstagram
from app.features.instagram.services import InstagramService


instagram_router = Router()


# INSTAGRAM DOWNLOAD VIDEO
@instagram_router.message(F.text, IsInstagram())
@error_handler
async def process_instagram_download(message: Message):
    serv = InstagramService(message)
    await serv.process_instagram_content()
