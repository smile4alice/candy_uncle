from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from src.filters.admin import IsSuperuser


config_router = Router()


@config_router.message(Command(commands=["config"]), IsSuperuser())
async def process_config(message: Message):
    await message.answer(text="handled config for superuser")
