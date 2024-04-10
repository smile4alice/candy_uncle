from aiogram.filters.callback_data import CallbackData


class CancelTriggerCallback(CallbackData, prefix="cancel_rect"):
    user_message_id: int
    chat_id: int


class DeleteTriggerCallback(CallbackData, prefix="delete_rect"):
    rect_id: int
