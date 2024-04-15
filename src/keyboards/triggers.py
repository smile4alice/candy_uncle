from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.filters.callback_data.rect_callback import (
    CancelTriggerCallback,
    DeleteTriggerCallback,
)


def get_cancel_state_keyboard(message_id: int, chat_id: int) -> InlineKeyboardMarkup:
    cancel_button = InlineKeyboardButton(
        text="скасувати❌",
        callback_data=CancelTriggerCallback(
            user_message_id=message_id,
            chat_id=chat_id,
        ).pack(),
    )
    keyboard = InlineKeyboardMarkup(row_width=5, inline_keyboard=[[cancel_button]])
    return keyboard


def get_trigger_keyboards(trigger_name: str) -> InlineKeyboardMarkup:
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
        inline_keyboard=[[keyboard_text], [keyboard_animation], [keyboard_sticker]]
    )
    return keyboards


def get_manage_answer_keyboards(
    trigger_name: str, answer_id: int, edit_data: str | None = None
) -> InlineKeyboardMarkup:
    delete_button = InlineKeyboardButton(
        text=f"❌delete_trigger_{trigger_name}_{answer_id}",
        callback_data=DeleteTriggerCallback(rect_id=answer_id).pack(),
    )
    list_of_button = [delete_button]
    if edit_data:
        edit_button = InlineKeyboardButton(
            text="✏️edit_trigger",
            switch_inline_query_current_chat=f"#edit_trigger_{trigger_name}_text_{answer_id}\n{edit_data}",
        )
        list_of_button.append(edit_button)
    keyboards = InlineKeyboardMarkup(inline_keyboard=[list_of_button])
    return keyboards
