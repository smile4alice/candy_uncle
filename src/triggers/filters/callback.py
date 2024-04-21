from aiogram.filters.callback_data import CallbackData


class CancelStateCallback(CallbackData, prefix="cancel_rect"):
    msg_id_which_run_state: int
    delete_it: bool


class DeleteTriggerCallback(CallbackData, prefix="delete_rect"):
    trigger_id: int


class AnotherOneTriggerCallback(CallbackData, prefix="put_trigger"):
    trigger_event: str
