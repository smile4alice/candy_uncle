from aiogram import F, Router
from aiogram.types import Message

from src.roll.services import RollService


roll_router = Router()


@roll_router.message(F.text.startswith("/rol") | F.text.startswith("/рол"))
async def process_roll(message: Message):
    serv = RollService()
    roll = serv.get_roll(message.text)  # type: ignore
    text = serv.to_text_from_user(message.from_user, roll)  # type: ignore
    await message.answer(text=text)
