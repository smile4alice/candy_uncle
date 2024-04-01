from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from src.services.base_commands_service import get_text_by_command_name


base_commands_router = Router()


# START
@base_commands_router.message(CommandStart())
async def process_start(message: Message):
    text = await get_text_by_command_name("start")
    await message.reply(text=text)
