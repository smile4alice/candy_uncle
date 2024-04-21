from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (
    CallbackQuery,
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultCachedGif,
    InlineQueryResultCachedSticker,
    InputTextMessageContent,
    Message,
)

from src.enums import MediaTypeEnum

from .filters.callback import (
    AnotherOneTriggerCallback,
    CancelStateCallback,
    DeleteTriggerCallback,
)
from .filters.fsm_states import FSMRect
from .filters.message import IsTrigger
from .keyboards import (
    get_another_one_trigger_keyboards,
    get_cancel_state_keyboards,
    get_manage_answer_keyboards,
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
async def process_trigger_categories(message: Message):
    result = await TriggerService.get_trigger_event_from_command(
        message.text, chat_id=message.chat.id  # type: ignore
    )
    if isinstance(result, TriggerEvent):
        keyboards = get_trigger_keyboards(result.name, chat_id=message.chat.id)
        text = f"Select media type for trigger <code>{result.name}</code>"
        await message.answer(text=text, reply_markup=keyboards)
    else:
        await message.answer(text=result)


@triggers_router.inline_query(
    lambda inline_query: any(
        i in inline_query.query for i in ["text", "animation", "sticker"]
    )
)
async def process_triggers_inline_query(inline_query: InlineQuery):
    items_per_page = 10
    command_data = inline_query.query.split("_")  # chat_id_event_media_type
    if not (len(command_data) == 3 and command_data[0].isdigit()):
        return
    chat_id = int(command_data[0])
    event_name = command_data[1]
    media_type = MediaTypeEnum(command_data[2])
    result = await TriggerService.get_triggers_for_inline(
        event_name=event_name,
        chat_id=chat_id,
        media_type=media_type,
        items_per_page=items_per_page,
        offset=inline_query.offset,
    )
    if isinstance(result, tuple):
        next_offset, records_list = result
    else:
        records_list = []

    inline_list = list()
    if records_list:
        if media_type == MediaTypeEnum.TEXT:
            for record in records_list:
                inline_list.append(
                    InlineQueryResultArticle(
                        id=f"trigger_{record.id}",
                        title=record.media,
                        description=f"#{record.id}",
                        input_message_content=InputTextMessageContent(
                            message_text=record.media,
                        ),
                        thumb_url="https://repository-images.githubusercontent.com/515040297/b1d94f1e-26ef-4b0a-8601-9b139ee5c5cc",
                        reply_markup=get_manage_answer_keyboards(
                            trigger_event=event_name,
                            trigger_id=record.id,
                        ),
                    )
                )
        if media_type == MediaTypeEnum.ANIMATION:
            for record in records_list:
                inline_list.append(
                    InlineQueryResultCachedGif(  # type: ignore
                        id=f"rect_{record.id}",
                        gif_file_id=record.media,
                        reply_markup=get_manage_answer_keyboards(
                            trigger_event=event_name,
                            trigger_id=record.id,
                        ),
                    )
                )
        if media_type == MediaTypeEnum.STICKER:
            for record in records_list:
                inline_list.append(
                    InlineQueryResultCachedSticker(  # type: ignore
                        id=f"rect_{record.id}",
                        title=record.media,
                        sticker_file_id=record.media,
                        reply_markup=get_manage_answer_keyboards(
                            trigger_event=event_name,
                            trigger_id=record.id,
                        ),
                    )
                )
    if inline_list:
        await inline_query.answer(
            results=inline_list, cache_time=5, next_offset=next_offset  # type: ignore #TODO
        )


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


@triggers_router.callback_query(DeleteTriggerCallback.filter())
async def process_delete_trigger(
    callback_query: CallbackQuery,
    callback_data: DeleteTriggerCallback,
):
    result = await TriggerService.delete_trigger(callback_data.trigger_id)
    await callback_query.answer(text=result)


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
