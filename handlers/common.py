from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.inline import main_menu_kb

router = Router()


@router.message()
async def handle_any_message(message: Message, state: FSMContext):
    """Обработка любых сообщений вне состояний"""
    current_state = await state.get_state()

    if current_state is None:
        # Если нет активного состояния, предлагаем начать
        await message.answer(
            "Используйте кнопки ниже для навигации:",
            reply_markup=main_menu_kb()
        )