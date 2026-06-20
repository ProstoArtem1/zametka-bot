import asyncio
import logging

from datetime import datetime

from aiogram import (
    Bot,
    Dispatcher,
    F
)

from aiogram.filters import (
    Command,
    CommandStart
)

from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN
from database import *
from keyboards import main_menu
from states import CreateNote


logging.basicConfig(
    filename="logs/bot.log",
    level=logging.INFO,
    encoding="utf-8",
    format="%(asctime)s | %(levelname)s | %(message)s"
)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):

    add_user(
        message.from_user.id,
        message.from_user.username,
        datetime.now().strftime("%d.%m.%Y %H:%M")
    )

    await message.answer(
        """
✨ Добро пожаловать в Notes Bot

Доступные команды:

/start - запуск
/help - инструкция
/list - мои заметки
/delete - удалить заметку
/stats - статистика

Используйте кнопки ниже 👇
""",
        reply_markup=main_menu
    )


@dp.message(Command("help"))
async def help_command(message: Message):

    await message.answer(
        """
📖 Инструкция

1. Создайте заметку

2. Введите название

3. Введите текст

4. Заметка сохранится в базе

Команды:

/list
/delete
/stats
"""
    )


@dp.message(Command("stats"))
async def stats(message: Message):

    count = get_notes_count(
        message.from_user.id
    )

    await message.answer(
        f"""
📊 Статистика

📝 Заметок: {count}
🆔 Ваш ID: {message.from_user.id}
"""
    )


@dp.message(F.text == "📝 Создать заметку")
async def create_note(message: Message, state: FSMContext):

    await message.answer(
        "Введите название заметки:"
    )

    await state.set_state(
        CreateNote.title
    )


@dp.message(CreateNote.title)
async def note_title(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        title=message.text
    )

    await message.answer(
        "Введите текст заметки:"
    )

    await state.set_state(
        CreateNote.text
    )


@dp.message(CreateNote.text)
async def note_text(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    add_note(
        message.from_user.id,
        data["title"],
        message.text,
        datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )
    )

    logging.info(
        f"User {message.from_user.id} created note"
    )

    await message.answer(
        "✅ Заметка сохранена!"
    )

    await state.clear()


@dp.message(Command("list"))
@dp.message(F.text == "📚 Мои заметки")
async def list_notes(message: Message):

    notes = get_notes(
        message.from_user.id
    )

    if not notes:

        await message.answer(
            "❌ Заметок пока нет."
        )

        return

    buttons = []

    # вложенный цикл специально для проекта
    for note in notes:

        row = []

        for i in range(1):

            row.append(
                InlineKeyboardButton(
                    text=note[2],
                    callback_data=f"note_{note[0]}"
                )
            )

        buttons.append(row)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )

    await message.answer(
        "📚 Ваши заметки:",
        reply_markup=keyboard
    )


@dp.callback_query(
    F.data.startswith("note_")
)
async def show_note(
    callback: CallbackQuery
):

    note_id = int(
        callback.data.split("_")[1]
    )

    note = get_note(note_id)

    if not note:
        await callback.answer(
            "Заметка не найдена.",
            show_alert=True
        )
        return

    if note[1] != callback.from_user.id:
        await callback.answer(
            "Это не ваша заметка!",
            show_alert=True
        )
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"delete_{note_id}"
                )
            ]
        ]
    )

    await callback.message.answer(
        f"""
📌 Название:
{note[2]}

📝 Текст:
{note[3]}

📅 Создана:
{note[4]}
""",
        reply_markup=keyboard
    )

    await callback.answer()


@dp.message(Command("delete"))
async def delete_command(
    message: Message
):

    notes = get_notes(
        message.from_user.id
    )

    if not notes:

        await message.answer(
            "❌ Нет заметок."
        )

        return

    buttons = []

    for note in notes:

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"🗑 {note[2]}",
                    callback_data=f"delete_{note[0]}"
                )
            ]
        )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )

    await message.answer(
        "Выберите заметку:",
        reply_markup=keyboard
    )


@dp.callback_query(
    F.data.startswith("delete_")
)
async def delete_callback(
    callback: CallbackQuery
):

    note_id = int(
        callback.data.split("_")[1]
    )

    note = get_note(note_id)

    if not note:
        await callback.answer(
            "Заметка не найдена.",
            show_alert=True
        )
        return

    if note[1] != callback.from_user.id:
        await callback.answer(
            "Это не ваша заметка!",
            show_alert=True
        )
        return

    delete_note(note_id)

    logging.info(
        f"User {callback.from_user.id} deleted note {note_id}"
    )

    await callback.message.edit_text(
        "✅ Заметка удалена."
    )

    await callback.answer()


async def main():

    logging.info(
        "Bot started"
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())