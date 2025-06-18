from aiogram.fsm.state import State, StatesGroup

class StateSend(StatesGroup):
    text_send: State = State()