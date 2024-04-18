from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .filters.callback import (
    AnotherOneTriggerCallback,
    CancelStateCallback,
    DeleteTriggerCallback,
)


def get_cancel_state_keyboards(bot_message_id: int) -> InlineKeyboardMarkup:
    cancel_button = InlineKeyboardButton(
        text="✖️cancel",
        callback_data=CancelStateCallback(
            bot_message_id=bot_message_id,
        ).pack(),
    )
    keyboards = InlineKeyboardMarkup(row_width=5, inline_keyboard=[[cancel_button]])
    return keyboards


def get_trigger_keyboards(
    trigger_name: str,
) -> InlineKeyboardMarkup:
    keyboard_text = InlineKeyboardButton(
        text="text",
        switch_inline_query_current_chat=f"#{trigger_name}_text",
    )
    keyboard_animation = InlineKeyboardButton(
        text="animation",
        switch_inline_query_current_chat=f"#{trigger_name}_animation",
    )
    keyboard_sticker = InlineKeyboardButton(
        text="sticker",
        switch_inline_query_current_chat=f"#{trigger_name}_sticker",
    )
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=[
            [keyboard_text],
            [keyboard_animation],
            [keyboard_sticker],
        ]
    )
    return keyboards


def get_manage_answer_keyboards(
    trigger_event: str,
    trigger_id: int,
) -> InlineKeyboardMarkup:
    delete_button = InlineKeyboardButton(
        text=f"❌delete_trigger_{trigger_event}_{trigger_id}",
        callback_data=DeleteTriggerCallback(rect_id=trigger_id).pack(),
    )
    list_of_button = [delete_button]
    keyboards = InlineKeyboardMarkup(inline_keyboard=[list_of_button])
    return keyboards


def get_another_one_trigger_keyboards(
    trigger_event: str,
) -> InlineKeyboardMarkup:
    callback_data = AnotherOneTriggerCallback(trigger_event=trigger_event).pack()
    another_button = InlineKeyboardButton(
        text="🔄another one",
        callback_data=callback_data,
    )
    list_of_button = [another_button]
    keyboards = InlineKeyboardMarkup(inline_keyboard=[list_of_button])
    return keyboards
