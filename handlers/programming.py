from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import logging
from keyboards.inline import language_kb, format_kb, main_menu_kb, back_kb, main_menu_button_kb
from utils.notifications import notify_admin
from utils.context import context

router = Router()
logger = logging.getLogger('app')  # Используем наш кастомный логгер


class ProgrammingStates(StatesGroup):
    waiting_language = State()
    waiting_format = State()
    waiting_contact = State()


@router.callback_query(F.data == "programming_help")
async def programming_help_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Какой язык хотите изучать?",
        reply_markup=language_kb()
    )
    await state.set_state(ProgrammingStates.waiting_language)
    await callback.answer()


@router.callback_query(ProgrammingStates.waiting_language, F.data.startswith("lang_"))
async def language_selected(callback: CallbackQuery, state: FSMContext):
    language = "C++" if callback.data == "lang_cpp" else "Python"

    await state.update_data(
        category="programming",
        language=language,
        username=callback.from_user.username,
        user_id=callback.from_user.id,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    await callback.message.answer(
        "Выберите формат занятий:",
        reply_markup=format_kb()
    )

    await state.set_state(ProgrammingStates.waiting_format)
    await callback.answer()


@router.callback_query(ProgrammingStates.waiting_format, F.data.startswith("format_"))
async def format_selected(callback: CallbackQuery, state: FSMContext):
    format_type = "индивидуально" if callback.data == "format_individual" else "в группе"

    await state.update_data(format=format_type)

    await callback.message.answer(
        "Пожалуйста, оставьте свой номер телефона или @ник в Telegram для связи.",
        reply_markup=back_kb("programming_help")
    )

    await state.set_state(ProgrammingStates.waiting_contact)
    await callback.answer()


@router.message(ProgrammingStates.waiting_contact)
async def process_programming_contact(message: Message, state: FSMContext):
    contact_info = message.text
    user_data = await state.get_data()

    # Логируем в том же формате что и aiogram
    logger.info(f"📋 Новый запрос на обучение:\n"
                f"👤 Пользователь: @{user_data.get('username')} (ID: {user_data.get('user_id')})\n"
                f"💻 Язык: {user_data.get('language')}\n"
                f"📚 Формат: {user_data.get('format')}\n"
                f"📞 Контакт: {contact_info}\n"
                f"{'=' * 50}")

    # Отправляем уведомление админу через context
    await notify_admin(context.bot, user_data, contact_info)

    # Отправляем подтверждение пользователю С КНОПКОЙ
    await message.answer(
        "✅ Спасибо! Мы свяжемся с вами в течение 15 минут.\n\n"
        "🎁 Пока ждёте, можете скачать бонус: [ссылка на PDF]",
        reply_markup=main_menu_button_kb()
    )

    # Планируем автосообщения через context
    await context.auto_message_scheduler.schedule_auto_messages(message.from_user.id)

    await state.clear()