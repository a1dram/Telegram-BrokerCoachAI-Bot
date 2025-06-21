from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    msg = State()
    new_dialog = State()
    register = State()
    register_phone = State()
