from aiogram.fsm.state import StatesGroup, State


class User(StatesGroup):
    dish = State()
    massa = State()