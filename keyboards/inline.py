from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Главное меню
def main_menu_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🎓 Помощь студентам", callback_data="student_help"),
        InlineKeyboardButton(text="💻 Обучение программированию", callback_data="programming_help")
    )
    return keyboard.adjust(1).as_markup()

# Меню помощи студентам
def student_help_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="📝 Лабораторные", callback_data="work_labs"),
        InlineKeyboardButton(text="📊 Курсовые", callback_data="work_coursework"),
        InlineKeyboardButton(text="🎓 Дипломные", callback_data="work_diploma"),
        InlineKeyboardButton(text="❔ Другое", callback_data="work_other"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")
    )
    return keyboard.adjust(1).as_markup()

# Меню выбора языка
def language_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="C++", callback_data="lang_cpp"),
        InlineKeyboardButton(text="Python", callback_data="lang_python"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")
    )
    return keyboard.adjust(2, 1).as_markup()

# Меню формата обучения
def format_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="👤 Онлайн индивидуально", callback_data="format_individual"),
        InlineKeyboardButton(text="👥 Онлайн в группе", callback_data="format_group"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="programming_help")
    )
    return keyboard.adjust(1).as_markup()

# Кнопка только "Назад"
def back_kb(target: str = "main_menu"):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data=target))
    return keyboard.as_markup()

# Клавиатура для подтверждения с кнопкой в главное меню
def main_menu_button_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu")
    )
    return keyboard.as_markup()