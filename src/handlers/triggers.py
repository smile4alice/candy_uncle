from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.filters.triggers import IsTrigger
from src.services.triggers import TriggersService


triggers_router: Router = Router()


@triggers_router.message(IsTrigger())
async def process_triggers(message: Message):
    answer = await TriggersService.get_answer(text=message.text, chat_id=message.chat.id)  # type: ignore
    await message.reply(text=answer)


@triggers_router.message(Command("update_trigger"))
async def process_update_trigger(message: Message):
    res = await TriggersService.update_or_add_trigger(text=message.text, chat_id=message.chat.id)  # type: ignore
    await message.reply(text=res)


@triggers_router.message(Command("delete_trigger"))
async def process_delete_trigger(message: Message):
    serv = TriggersService()
    res = await serv.delete_trigger(text=message.text, chat_id=message.chat.id)  # type: ignore
    await message.reply(text=res)
