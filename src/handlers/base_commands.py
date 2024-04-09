from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.filters.commands import IsCommand
from src.services.base_commands import CommandService


base_commands_router = Router()


# UPDATE COMMAND
@base_commands_router.message(Command("update_command"))
async def process_update_command(message: Message):
    text = await CommandService.update_or_add_command(message.text)  # type: ignore
    await message.reply(text=text)


# DELETE COMMAND
@base_commands_router.message(Command("delete_command"))
async def process_delete_command(message: Message):
    text = await CommandService.delete_command(message.text)  # type: ignore
    await message.reply(text=text)


# GET COMMANDS
@base_commands_router.message(IsCommand())
async def process_commands(message: Message):
    text = await CommandService.get_command_text(message.text)  # type: ignore
    await message.reply(text=text)
