from aiogram.filters.callback_data import CallbackData


class CancelStateCallback(CallbackData, prefix="cancel_rect"):
    bot_message_id: int


class DeleteTriggerCallback(CallbackData, prefix="delete_rect"):
    rect_id: int


class AnotherOneTriggerCallback(CallbackData, prefix="put_trigger"):
    trigger_event: str
