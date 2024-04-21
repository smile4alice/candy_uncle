from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from .filters import IsCommand
from .services import InfoCommandService


info_commands_router = Router()


@info_commands_router.message(Command("put_command"))
async def process_put_command(message: Message):
    text = await InfoCommandService.put_command(message.text, message.chat.id)  # type: ignore
    await message.reply(text=text)


@info_commands_router.message(Command("delete_command"))
async def process_delete_command(message: Message):
    text = await InfoCommandService.delete_command(message.text, message.chat.id)  # type: ignore
    await message.reply(text=text)


@info_commands_router.message(F.text.startswith("/"), IsCommand())
async def process_use_command(message: Message):
    text = await InfoCommandService.use_command(message.text, message.chat.id)  # type: ignore
    await message.reply(text=text)
