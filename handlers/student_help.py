from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import logging
from keyboards.inline import student_help_kb, main_menu_kb, back_kb, main_menu_button_kb
from utils.notifications import notify_admin
from utils.context import context

router = Router()
logger = logging.getLogger('app')  # Используем наш кастомный логгер


class StudentStates(StatesGroup):
    waiting_contact = State()


@router.callback_query(F.data == "student_help")
async def student_help_start(callback: CallbackQuery):
    await callback.message.answer(
        "Какие работы нужны?",
        reply_markup=student_help_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("work_"))
async def student_work_selected(callback: CallbackQuery, state: FSMContext):
    work_types = {
        "work_labs": "Лабораторные",
        "work_coursework": "Курсовые",
        "work_diploma": "Дипломные",
        "work_other": "Другое"
    }

    work_type = work_types.get(callback.data, "Другое")

    await state.update_data(
        category="student_help",
        work_type=work_type,
        username=callback.from_user.username,
        user_id=callback.from_user.id,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    await callback.message.answer(
        "Пожалуйста, оставьте свой номер телефона или @ник в Telegram для связи.",
        reply_markup=back_kb("student_help")
    )

    await state.set_state(StudentStates.waiting_contact)
    await callback.answer()


@router.message(StudentStates.waiting_contact)
async def process_student_contact(message: Message, state: FSMContext):
    contact_info = message.text
    user_data = await state.get_data()

    # Логируем в том же формате что и aiogram
    logger.info(f"📋 Новый запрос от студента:\n"
                f"👤 Пользователь: @{user_data.get('username')} (ID: {user_data.get('user_id')})\n"
                f"📝 Тип работы: {user_data.get('work_type')}\n"
                f"📞 Контакт: {contact_info}\n"
                f"{'=' * 50}")

    # Отправляем уведомление админу через context
    await notify_admin(context.bot, user_data, contact_info)

    # Отправляем подтверждение пользователю С КНОПКОЙ
    await message.answer(
        "✅ Спасибо! Мы свяжемся с вами в течение 15 минут.",
        reply_markup=main_menu_button_kb()
    )

    # Планируем автосообщения через context
    await context.auto_message_scheduler.schedule_auto_messages(message.from_user.id)

    await state.clear()