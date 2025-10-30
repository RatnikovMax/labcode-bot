from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from keyboards.inline import main_menu_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = """
👋 Привет! Это Lab&Code.

Мы помогаем:
📚 Студентам — с лабораторными, курсовыми, дипломами
💻 Всем, кто хочет освоить C++ или Python

Что вас интересует?
    """

    await message.answer(welcome_text, reply_markup=main_menu_kb())


@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    welcome_text = """
👋 С возвращением в Lab&Code!

Что вас интересует?
    """

    await callback.message.answer(welcome_text, reply_markup=main_menu_kb())
    await callback.answer()