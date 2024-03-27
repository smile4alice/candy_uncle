from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

default_router = Router()


# EXAMPLE
@default_router.message(CommandStart())
async def process_start(message: Message):
    await message.reply(text="Start command successfully processed.")
