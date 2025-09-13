"""Roll routes."""

from aiogram import F, Router
from aiogram.types import Message

from app.common.utils import error_handler
from app.features.roll.services import RollService


router = Router()


@router.message(F.text.startswith("/rol") | F.text.startswith("/рол"))
@error_handler
async def process_roll(message: Message):
    serv = RollService(message)
    await serv.process_roll_command()
