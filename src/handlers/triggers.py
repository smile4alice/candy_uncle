from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message

from src.enums import MediaTypeEnum
from src.exceptions import InvalidCommandError
from src.filters.callback_data.rect_callback import CancelTriggerCallback
from src.filters.triggers import IsTrigger
from src.fsm_states.rect_states import FSMRect
from src.keyboards.triggers import (
    get_cancel_state_keyboard,
    get_trigger_keyboards,
)
from src.services.triggers import TriggerAnswerService, TriggerService


triggers_router: Router = Router()


# TRIGGERS PUT
@triggers_router.message(Command("triggers_put"))
async def process_triggers_put(message: Message):
    res = await TriggerService.put_trigger(text=message.text, chat_id=message.chat.id)  # type: ignore
    await message.reply(text=res)


# TRIGGER DELETE
@triggers_router.message(Command("triggers_delete"))
async def process_triggers_delete(message: Message):
    res = await TriggerService.delete_trigger(text=message.text, chat_id=message.chat.id)  # type: ignore
    await message.reply(text=res)


# UPDATE ANSWER
@triggers_router.message(Command(commands=["put_answer"]), StateFilter(default_state))
async def process_put_answer(message: Message, state: FSMContext):
    try:
        command_data = message.text.split()
        if len(command_data) < 2:
            raise InvalidCommandError(example="`/put_answer <trigger>`")
        else:
            trigger_name = command_data[1]
            markup = get_cancel_state_keyboard(
                message_id=message.message_id, chat_id=message.chat.id
            )
            old_bot_message = await message.answer(
                text=f"Waiting response for trigger /{trigger_name}/",
                reply_markup=markup,
            )
            await state.set_state(FSMRect.wait_put_answer)
            await state.set_data(
                {
                    "old_user_put_answer": {
                        "message_id": message.message_id,
                        "chat_id": message.chat.id,
                    },
                    "old_bot_put_answer": {
                        "message_id": old_bot_message.message_id,
                        "chat_id": old_bot_message.chat.id,
                    },
                    "trigger_name": trigger_name,
                }
            )
    except InvalidCommandError as e:
        await message.answer(text=str(e))


# CANCEL STATE
@triggers_router.callback_query(CancelTriggerCallback.filter(F.user_message_id))
async def cancel_put_trigger(
    callback_query: CallbackQuery,
    callback_data: CancelTriggerCallback,
    state: FSMContext,
):
    await callback_query.message.delete()
    await callback_query.bot.delete_message(
        chat_id=callback_data.chat_id, message_id=callback_data.user_message_id
    )
    await state.set_state()


# FSM CREATE ANSWER
@triggers_router.message(StateFilter(FSMRect.wait_put_answer))
async def process_put_answer_fsm(message: Message, state: FSMContext):
    state_data = await state.get_data()
    trigger_name = state_data["trigger_name"]
    await state.set_state()

    media = None
    media_type = MediaTypeEnum(message.content_type.value)  # type: ignore

    if media_type == MediaTypeEnum.TEXT:
        media = message.text
    elif media_type == MediaTypeEnum.ANIMATION:
        media = message.animation.file_id
    elif media_type == MediaTypeEnum.STICKER:
        media = message.sticker.file_id

    if media:
        text = await TriggerAnswerService.put_answer(
            trigger_name=trigger_name,
            chat_id=message.chat.id,
            media_type=media_type,
            media=media,
        )
        old_data = await state.get_data()
        old_bot_put_answer = old_data["old_bot_put_answer"]
        await message.bot.delete_message(
            chat_id=old_bot_put_answer["chat_id"],
            message_id=old_bot_put_answer["message_id"],
        )
        old_user_put_answer = old_data["old_user_put_answer"]
        await message.bot.delete_message(
            chat_id=old_user_put_answer["chat_id"],
            message_id=old_user_put_answer["message_id"],
        )
    else:
        text = (
            f"`{media_type}` is not a supported type for triggers - operation canceled"
        )

    await message.reply(text=text)


# TRIGGER
@triggers_router.message(Command("trigger"), StateFilter(default_state))
async def process_trigger(message: Message):
    command_data = message.text.split()  # type: ignore
    try:
        if len(command_data) < 2:
            raise InvalidCommandError(example="`/trigger <trigger_name>`")
        else:
            trigger_name = command_data[1]
            keyboards = get_trigger_keyboards(trigger_name)
            text = f"Select media type for trigger `/{trigger_name}/`"
            await message.answer(text=text, reply_markup=keyboards)
    except InvalidCommandError as e:
        await message.answer(text=str(e))


# GET TRIGGER
@triggers_router.message(F.text, StateFilter(default_state), IsTrigger())
async def process_triggers(message: Message):
    result = await TriggerAnswerService.get_answer(text=message.text, chat_id=message.chat.id)  # type: ignore
    if isinstance(result, str):
        await message.answer(text=result)
    else:
        if result.media_type == MediaTypeEnum.TEXT:
            await message.reply(text=result.answer)
        elif result.media_type == MediaTypeEnum.ANIMATION:
            await message.reply_animation(animation=result.answer)
        elif result.media_type == MediaTypeEnum.STICKER:
            await message.reply_sticker(sticker=result.answer)


# MOCK CALLBACK
@triggers_router.callback_query(lambda callback_query: callback_query.data == "mock")
async def mock_callback(callback_query: CallbackQuery):
    await callback_query.answer()
