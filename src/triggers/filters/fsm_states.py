from aiogram.fsm.state import State, StatesGroup


class FSMRect(StatesGroup):
    wait_put_answer = State()
