# utils/notifications.py
import logging
from aiogram import Bot
from config import ADMIN_ID, VK_ADMIN_ID, VK_GROUP_TOKEN
import vk_api
from datetime import datetime

notification_logger = logging.getLogger('app')


async def notify_admin(bot: Bot, user_data: dict, contact_info: str):
    """Отправка уведомления администратору в Telegram"""
    if not ADMIN_ID:
        notification_logger.warning("ADMIN_ID не установлен. Уведомление не отправлено.")
        return

    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if user_data.get('category') == 'student_help':
            message_text = f"""
📋 **НОВЫЙ ЗАПРОС ОТ СТУДЕНТА**

👤 **Пользователь:** @{user_data.get('username', 'N/A')} (ID: {user_data.get('user_id', 'N/A')})
📝 **Тип работы:** {user_data.get('work_type', 'N/A')}
📞 **Контакт:** {contact_info}
🕐 **Время:** {timestamp}

⚡ **Требует быстрого ответа!**
            """
        else:
            message_text = f"""
📋 **НОВЫЙ ЗАПРОС НА ОБУЧЕНИЕ**

👤 **Пользователь:** @{user_data.get('username', 'N/A')} (ID: {user_data.get('user_id', 'N/A')})
💻 **Язык:** {user_data.get('language', 'N/A')}
📚 **Формат:** {user_data.get('format', 'N/A')}
📞 **Контакт:** {contact_info}
🕐 **Время:** {timestamp}

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
    if not VK_ADMIN_ID or not VK_GROUP_TOKEN:
        notification_logger.warning("VK_ADMIN_ID или VK_GROUP_TOKEN не установлены. Уведомление не отправлено.")
        return

    try:
        # Создаем новую сессию VK для отправки уведомления
        vk_session = vk_api.VkApi(token=VK_GROUP_TOKEN)
        vk = vk_session.get_api()

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if user_data.get('category') == 'student_help':
            message_text = f"""
📋 НОВЫЙ ЗАПРОС ОТ СТУДЕНТА (VK)

👤 Пользователь: VK ID: {user_id}
📝 Тип работы: {user_data.get('work_type', 'N/A')}
📞 Контакт: {contact_info}
🕐 Время: {timestamp}

⚡ Требует быстрого ответа!
            """
        else:
            message_text = f"""
📋 НОВЫЙ ЗАПРОС НА ОБУЧЕНИЕ (VK)

👤 Пользователь: VK ID: {user_id}
💻 Язык: {user_data.get('language', 'N/A')}
📚 Формат: {user_data.get('format', 'N/A')}
📞 Контакт: {contact_info}
🕐 Время: {timestamp}

⚡ Требует быстрого ответа!
            """

        # Отправляем сообщение администратору VK
        vk.messages.send(
            user_id=int(VK_ADMIN_ID),
            message=message_text,
            random_id=vk_api.utils.get_random_id()
        )

        notification_logger.info(f"VK уведомление отправлено админу {VK_ADMIN_ID} от пользователя {user_id}")

    except vk_api.exceptions.ApiError as e:
        notification_logger.error(f"VK API ошибка отправки уведомления админу: {e}")
    except Exception as e:
        notification_logger.error(f"Общая ошибка отправки VK уведомления админу: {e}")


# Альтернативная функция, если нужно использовать существующую VK сессию
def notify_admin_vk_with_session(vk_api_object, user_data: dict, contact_info: str, user_id: int):
    """Отправка уведомления администратору в VK с использованием существующего VK API объекта"""
    if not VK_ADMIN_ID:
        notification_logger.warning("VK_ADMIN_ID не установлен. Уведомление не отправлено.")
        return

    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if user_data.get('category') == 'student_help':
            message_text = f"""
📋 НОВЫЙ ЗАПРОС ОТ СТУДЕНТА (VK)

👤 Пользователь: VK ID: {user_id}
📝 Тип работы: {user_data.get('work_type', 'N/A')}
📞 Контакт: {contact_info}
🕐 Время: {timestamp}

⚡ Требует быстрого ответа!
            """
        else:
            message_text = f"""
📋 НОВЫЙ ЗАПРОС НА ОБУЧЕНИЕ (VK)

👤 Пользователь: VK ID: {user_id}
💻 Язык: {user_data.get('language', 'N/A')}
📚 Формат: {user_data.get('format', 'N/A')}
📞 Контакт: {contact_info}
🕐 Время: {timestamp}

⚡ Требует быстрого ответа!
            """

        # Используем переданный VK API объект
        vk_api_object.messages.send(
            user_id=int(VK_ADMIN_ID),
            message=message_text,
            random_id=vk_api.utils.get_random_id()
        )

        notification_logger.info(f"VK уведомление отправлено админу {VK_ADMIN_ID} от пользователя {user_id}")

    except Exception as e:
        notification_logger.error(f"Ошибка отправки VK уведомления админу: {e}")