# utils/notifications.py
import logging
from aiogram import Bot
from config import ADMIN_ID

# Логгер для уведомлений в том же формате
notification_logger = logging.getLogger('app')


async def notify_admin(bot: Bot, user_data: dict, contact_info: str):
    """Отправка уведомления администратору"""
    if not ADMIN_ID:
        notification_logger.warning("ADMIN_ID не установлен. Уведомление не отправлено.")
        return

    try:
        if user_data.get('category') == 'student_help':
            message_text = f"""
📋 **НОВЫЙ ЗАПРОС ОТ СТУДЕНТА**

👤 **Пользователь:** @{user_data.get('username', 'N/A')} (ID: {user_data.get('user_id', 'N/A')})
📝 **Тип работы:** {user_data.get('work_type', 'N/A')}
📞 **Контакт:** {contact_info}
🕐 **Время:** {user_data.get('timestamp', 'N/A')}

⚡ **Требует быстрого ответа!**
            """
        else:
            message_text = f"""
📋 **НОВЫЙ ЗАПРОС НА ОБУЧЕНИЕ**

👤 **Пользователь:** @{user_data.get('username', 'N/A')} (ID: {user_data.get('user_id', 'N/A')})
💻 **Язык:** {user_data.get('language', 'N/A')}
📚 **Формат:** {user_data.get('format', 'N/A')}
📞 **Контакт:** {contact_info}
🕐 **Время:** {user_data.get('timestamp', 'N/A')}

⚡ **Требует быстрого ответа!**
            """

        await bot.send_message(
            chat_id=ADMIN_ID,
            text=message_text,
            parse_mode='Markdown'
        )
        notification_logger.info(f"Уведомление отправлено админу {ADMIN_ID} от пользователя {user_data.get('user_id')}")

    except Exception as e:
        notification_logger.error(f"Ошибка отправки уведомления админу: {e}")