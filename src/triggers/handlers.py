from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message

from src.enums import MediaTypeEnum

from .filters.callback import AnotherOneTriggerCallback, CancelStateCallback
from .filters.fsm_states import FSMRect
from .filters.message import IsTrigger
from .keyboards import (
    get_another_one_trigger_keyboards,
    get_cancel_state_keyboards,
    get_trigger_keyboards,
)
from .models import Trigger, TriggerEvent
from .services import TriggerEventService, TriggerService


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


@triggers_router.callback_query(AnotherOneTriggerCallback.filter())
@triggers_router.message(Command(commands=["put_trigger"]), StateFilter(default_state))
async def process_put_trigger(
    event_object: Message | CallbackQuery,
    state: FSMContext,
    callback_data: AnotherOneTriggerCallback | None = None,
):
    if isinstance(event_object, CallbackQuery):
        text = f"/put_trigger {callback_data.trigger_event}"
        message = event_object.message
        await message.delete_reply_markup()
    else:
        message = event_object
        text = message.text  # type: ignore

    result = await TriggerService.get_trigger_event_from_command(text, message.chat.id)  # type: ignore
    if isinstance(result, TriggerEvent):
        delete_msg_which_run_state = message.from_user.is_bot == False  # noqa: E712
        markup = get_cancel_state_keyboards(
            msg_id_which_run_state=message.message_id,
            delete_it=delete_msg_which_run_state,
        )
        old_bot_message = await message.answer(
            text=f"Waiting media for <code>{result.name}</code>",
            reply_markup=markup,
        )
        await state.set_state(FSMRect.wait_put_answer)
        await state.set_data(
            {
                "bot_put_trigger_msg_id": old_bot_message.message_id,
                "trigger_event": result.name,
            }
        )
    else:
        await message.answer(text=result)


@triggers_router.message(StateFilter(FSMRect.wait_put_answer))
async def process_put_trigger_fsm(message: Message, state: FSMContext):
    state_data = await state.get_data()
    media = None
    media_type = MediaTypeEnum(message.content_type.value)  # type: ignore
    markup = get_another_one_trigger_keyboards(state_data["trigger_event"])

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
        await state.set_state()
    else:
        text = f"<code>{media_type}</code> is not a supported type for triggers. Try again."
    await message.reply(text=text, reply_markup=markup)


@triggers_router.message(Command("trigger"), StateFilter(default_state))
async def process_trigger_inline_list(message: Message):
    result = await TriggerService.get_trigger_event_from_command(
        message.text, chat_id=message.chat.id  # type: ignore
    )
    if isinstance(result, TriggerEvent):
        keyboards = get_trigger_keyboards(result.name)
        text = f"Select media type for trigger <code>{result.name}<code>"
        await message.answer(text=text, reply_markup=keyboards)
    else:
        await message.answer(text=result)


@triggers_router.message(F.text, StateFilter(default_state), IsTrigger())
async def process_trigger(message: Message):
    result = await TriggerService.get_trigger(
        text=message.text, chat_id=message.chat.id  # type: ignore
    )
    if isinstance(result, Trigger):
        if result.media_type == MediaTypeEnum.TEXT:
            await message.reply(text=result.media)
        elif result.media_type == MediaTypeEnum.ANIMATION:
            await message.reply_animation(animation=result.media)
        elif result.media_type == MediaTypeEnum.STICKER:
            await message.reply_sticker(sticker=result.media)
    else:
        await message.answer(text=result)


@triggers_router.callback_query(CancelStateCallback.filter(F.msg_id_which_run_state))
async def cancel_put_trigger(
    callback_query: CallbackQuery,
    callback_data: CancelStateCallback,
    state: FSMContext,
):
    if callback_data.delete_it:
        await callback_query.bot.delete_message(
            chat_id=callback_query.message.chat.id,
            message_id=callback_data.msg_id_which_run_state,
        )
    await callback_query.message.delete()
    await state.set_state()


@triggers_router.callback_query(lambda callback_query: callback_query.data == "mock")
async def mock_callback(callback_query: CallbackQuery):
    await callback_query.answer()
