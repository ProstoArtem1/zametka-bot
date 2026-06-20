from aiogram.fsm.state import (
    State,
    StatesGroup
)

class CreateNote(StatesGroup):

    title = State()
    text = State()