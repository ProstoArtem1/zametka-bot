from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📝 Создать заметку"
            )
        ],
        [
            KeyboardButton(
                text="📚 Мои заметки"
            )
        ]
    ],
    resize_keyboard=True
)