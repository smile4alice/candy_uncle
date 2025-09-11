"""Roll routes."""

from aiogram import F, Router
from aiogram.types import Message

from app.common import error_handler, RollProcessingError
from app.features.roll.services import RollService


roll_router = Router()


@roll_router.message(F.text.startswith("/rol") | F.text.startswith("/рол"))
@error_handler
async def process_roll(message: Message):
    serv = RollService(message)
    await serv.process_roll_command()
