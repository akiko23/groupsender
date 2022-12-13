from aiogram.dispatcher.filters.state import StatesGroup, State


class AllStates(StatesGroup):
    set_interval = State()
    set_message = State()
    add_group = State()
