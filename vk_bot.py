# vk_bot.py
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import logging
import json
import asyncio
from datetime import datetime

from config import VK_GROUP_TOKEN, VK_GROUP_ID, VK_ADMIN_ID
from utils.auto_messages import AutoMessageScheduler
from utils.notifications import notify_admin_vk

logger = logging.getLogger(__name__)


class VKBot:
    def __init__(self):
        try:
            logger.info("🔄 Создание VK сессии...")
            self.vk_session = vk_api.VkApi(token=VK_GROUP_TOKEN)
            logger.info("🔄 Инициализация LongPoll...")
            self.longpoll = VkBotLongPoll(self.vk_session, int(VK_GROUP_ID))
            logger.info("🔄 Получение VK API...")
            self.vk = self.vk_session.get_api()
            self.user_states = {}
            self.user_data = {}
            self.auto_message_scheduler = AutoMessageScheduler()
            logger.info("✅ VK бот инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации VK бота: {e}", exc_info=True)
            raise

    # ... остальной код без изменений (get_keyboard, handle_start и т.д.)

    def run(self):
        """Запуск VK бота"""
        logger.info("🚀 VK бот запущен, ожидаем сообщения...")

        try:
            # Проверяем подключение
            group_info = self.vk.groups.getById(group_id=int(VK_GROUP_ID))
            logger.info(f"✅ Подключение к группе: {group_info[0]['name']}")

            for event in self.longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW and not event.object.message.get('from_id') < 0:
                    user_id = event.object.message['from_id']
                    text = event.object.message['text'].lower().strip()

                    logger.info(f"📨 VK сообщение от {user_id}: {text}")

                    current_state = self.user_states.get(user_id, "main_menu")

                    # Обработка команд
                    if text in ['/start', 'start', 'начать', 'старт', 'привет']:
                        self.handle_start(user_id)

                    # Главное меню
                    elif current_state == "main_menu":
                        if "помощь студентам" in text or "🎓" in text:
                            self.handle_student_help(user_id)
                        elif "обучение программированию" in text or "💻" in text:
                            self.handle_programming_help(user_id)
                        else:
                            self.handle_start(user_id)

                    # Помощь студентам
                    elif current_state == "student_help":
                        if "лабораторные" in text or "📝" in text:
                            self.handle_work_type(user_id, "лабораторные")
                        elif "курсовые" in text or "📊" in text:
                            self.handle_work_type(user_id, "курсовые")
                        elif "дипломные" in text or "🎓" in text:
                            self.handle_work_type(user_id, "дипломные")
                        elif "другое" in text or "❔" in text:
                            self.handle_work_type(user_id, "другое")
                        elif "назад" in text or "⬅️" in text:
                            self.handle_back(user_id)
                        else:
                            self.handle_student_help(user_id)

                    # Выбор языка программирования
                    elif current_state == "programming_language":
                        if "c++" in text:
                            self.handle_language_choice(user_id, "c++")
                        elif "python" in text:
                            self.handle_language_choice(user_id, "python")
                        elif "назад" in text or "⬅️" in text:
                            self.handle_back(user_id)
                        else:
                            self.handle_programming_help(user_id)

                    # Выбор формата обучения
                    elif current_state == "programming_format":
                        if "индивидуально" in text or "👤" in text:
                            self.handle_format_choice(user_id, "индивидуально")
                        elif "в группе" in text or "👥" in text:
                            self.handle_format_choice(user_id, "в группе")
                        elif "назад" in text or "⬅️" in text:
                            self.handle_programming_help(user_id)
                        else:
                            self.send_message(user_id, "Выберите формат занятий:", self.get_format_keyboard())

                    # Ожидание контакта
                    elif current_state == "waiting_contact":
                        self.handle_contact_info(user_id, text)

                    # Возврат в главное меню
                    elif "в главное меню" in text or "🏠" in text:
                        self.handle_start(user_id)

                    # Любое другое сообщение
                    else:
                        self.handle_start(user_id)

        except Exception as e:
            logger.error(f"❌ Ошибка в VK боте: {e}", exc_info=True)