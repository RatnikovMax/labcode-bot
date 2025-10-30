# utils/notifications.py
import logging
from aiogram import Bot
from config import ADMIN_ID, VK_ADMIN_ID

notification_logger = logging.getLogger('app')


async def notify_admin(bot: Bot, user_data: dict, contact_info: str):
    """Отправка уведомления администратору в Telegram"""
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


def notify_admin_vk(user_data: dict, contact_info: str, user_id: int):
    """Отправка уведомления администратору в VK"""
    if not VK_ADMIN_ID:
        notification_logger.warning("VK_ADMIN_ID не установлен. Уведомление не отправлено.")
        return

    try:
        if user_data.get('category') == 'student_help':
            message_text = f"""
📋 НОВЫЙ ЗАПРОС ОТ СТУДЕНТА (VK)

👤 Пользователь: VK ID: {user_id}
📝 Тип работы: {user_data.get('work_type', 'N/A')}
📞 Контакт: {contact_info}
🕐 Время: {user_data.get('timestamp', 'N/A')}

⚡ Требует быстрого ответа!
            """
        else:
            message_text = f"""
📋 НОВЫЙ ЗАПРОС НА ОБУЧЕНИЕ (VK)

👤 Пользователь: VK ID: {user_id}
💻 Язык: {user_data.get('language', 'N/A')}
📚 Формат: {user_data.get('format', 'N/A')}
📞 Контакт: {contact_info}
🕐 Время: {user_data.get('timestamp', 'N/A')}

⚡ Требует быстрого ответа!
            """

        # Здесь будет код для отправки сообщения в VK
        # Нужно импортировать vk_api и отправить сообщение администратору
        notification_logger.info(f"VK уведомление для админа {VK_ADMIN_ID}: {message_text}")

    except Exception as e:
        notification_logger.error(f"Ошибка отправки VK уведомления админу: {e}")