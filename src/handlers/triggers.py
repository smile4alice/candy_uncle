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
from src.services.triggers import TriggerEventService, TriggerService


triggers_router: Router = Router()


@triggers_router.message(Command("put_trigger_event"))
async def process_put_trigger_event(message: Message):
    res = await TriggerEventService.put_trigger_event(
        text=message.text, chat_id=message.chat.id  # type: ignore
    )
    await message.reply(text=res)


@triggers_router.message(Command("delete_trigger_event"))
async def process_delete_trigger_event(message: Message):
    res = await TriggerEventService.delete_trigger_event(
        text=message.text, chat_id=message.chat.id  # type: ignore
    )
    await message.reply(text=res)


# UPDATE ANSWER
@triggers_router.message(
    Command(commands=["put_trigger"]),
    StateFilter(default_state),
)
async def process_put_trigger(message: Message, state: FSMContext):
    result = await TriggerService.wait_put_trigger(message.text, message.chat.id)  # type: ignore
    if isinstance(result, str):
        await message.answer(text=result)
    else:
        markup = get_cancel_state_keyboard(
            message_id=message.message_id,
            chat_id=message.chat.id,
        )
        old_bot_message = await message.answer(
            text=f"Waiting response for trigger /<code>{result.name}</code>/",
            reply_markup=markup,
        )
        await state.set_state(FSMRect.wait_put_answer)
        await state.set_data(
            {
                "user_put_trigger_msg_id": message.message_id,
                "bot_put_trigger_msg_id": old_bot_message.message_id,
                "trigger_event_name": result.name,
            }
        )


@triggers_router.message(StateFilter(FSMRect.wait_put_answer))
async def process_put_trigger_fsm(message: Message, state: FSMContext):
    state_data = await state.get_data()
    media = None
    media_type = MediaTypeEnum(message.content_type.value)  # type: ignore

    if media_type == MediaTypeEnum.TEXT:
        media = message.text
    elif media_type == MediaTypeEnum.ANIMATION:
        media = message.animation.file_id
    elif media_type == MediaTypeEnum.STICKER:
        media = message.sticker.file_id

    if media:
        text = await TriggerService.put_trigger(
            chat_id=message.chat.id,
            media_type=media_type,
            media=media,
            state_data=state_data,
        )
        await message.bot.delete_message(
            chat_id=message.chat.id,
            message_id=state_data["bot_put_trigger_msg_id"],
        )
        await message.bot.delete_message(
            chat_id=message.chat.id,
            message_id=state_data["user_put_trigger_msg_id"],
        )
        await state.set_state()
    else:
        text = f"<code>{media_type}</code> is not a supported type for triggers. Try again."
    await message.reply(text=text)


@triggers_router.message(Command("trigger"), StateFilter(default_state))
async def process_trigger_list(message: Message):
    command_data = message.text.split()
    try:
        if len(command_data) < 2:
            raise InvalidCommandError(example="<code>/trigger <trigger_name></code>")
        else:
            trigger_name = command_data[1]
            keyboards = get_trigger_keyboards(trigger_name)
            text = f"Select media type for trigger /<code>{trigger_name}<code>/"
            await message.answer(text=text, reply_markup=keyboards)
    except InvalidCommandError as e:
        await message.answer(text=str(e))


@triggers_router.message(F.text, StateFilter(default_state), IsTrigger())
async def process_trigger(message: Message):
    result = await TriggerService.get_trigger(
        text=message.text, chat_id=message.chat.id  # type: ignore
    )
    if isinstance(result, str):
        await message.answer(text=result)
    else:
        if result.media_type == MediaTypeEnum.TEXT:
            await message.reply(text=result.media)
        elif result.media_type == MediaTypeEnum.ANIMATION:
            await message.reply_animation(animation=result.media)
        elif result.media_type == MediaTypeEnum.STICKER:
            await message.reply_sticker(sticker=result.media)


@triggers_router.callback_query(CancelTriggerCallback.filter(F.user_message_id))
async def cancel_put_trigger(
    callback_query: CallbackQuery,
    callback_data: CancelTriggerCallback,
    state: FSMContext,
):
    await callback_query.message.delete()
    await callback_query.bot.delete_message(
        chat_id=callback_data.chat_id,
        message_id=callback_data.user_message_id,
    )
    await state.set_state()


@triggers_router.callback_query(lambda callback_query: callback_query.data == "mock")
async def mock_callback(callback_query: CallbackQuery):
    await callback_query.answer()
