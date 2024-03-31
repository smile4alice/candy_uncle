from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from src.exceptions import InvalidCommandError
from src.lib import SERVER_ERROR
from src.logging import LOGGER
from src.services.base_commands_service import update_or_add_record_by_name


admin_base_commands_router = Router()


# UPDATE BASE
@admin_base_commands_router.message(Command("update_base_command"))
async def process_update_command(message: Message):
    try:
        command_data = message.text.split() if message.text else []
        if len(command_data) <= 2:
            example = "/update_base_command start Hello. I'm a beautiful bot."
            raise InvalidCommandError(example=example)
        else:
            command_name = command_data[1]
            command_text = " ".join(command_data[2:])
            if await update_or_add_record_by_name(command_name, command_text):
                text = f"{command_name} command successfully update."
            else:
                text = SERVER_ERROR
            await message.reply(text=text)
    except InvalidCommandError as e:
        await message.reply(str(e))
    except Exception as e:
        LOGGER.exception(e)
