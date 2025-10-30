# vk_bot.py
import asyncio
import logging
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import json
from datetime import datetime

from config import VK_GROUP_TOKEN, VK_GROUP_ID, VK_ADMIN_ID
from utils.auto_messages import AutoMessageScheduler
from utils.notifications import notify_admin_vk
from utils.context import context

logger = logging.getLogger(__name__)


class VKBot:
    def __init__(self):
        self.vk_session = vk_api.VkApi(token=VK_GROUP_TOKEN)
        self.longpoll = VkBotLongPoll(self.vk_session, VK_GROUP_ID)
        self.vk = self.vk_session.get_api()
        self.user_states = {}
        self.user_data = {}

    def get_keyboard(self, buttons, inline=False):
        """Создание клавиатуры для VK"""
        keyboard = {
            "one_time": not inline,
            "buttons": buttons
        }
        return json.dumps(keyboard, ensure_ascii=False)

    def get_main_keyboard(self):
        """Главное меню для VK"""
        buttons = [
            [
                {
                    "action": {
                        "type": "text",
                        "payload": '{"button": "1"}',
                        "label": "🎓 Помощь студентам"
                    },
                    "color": "primary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "payload": '{"button": "2"}',
                        "label": "💻 Обучение программированию"
                    },
                    "color": "primary"
                }
            ]
        ]
        return self.get_keyboard(buttons)

    def get_student_keyboard(self):
        """Меню помощи студентам для VK"""
        buttons = [
            [
                {
                    "action": {
                        "type": "text",
                        "payload": '{"button": "labs"}',
                        "label": "📝 Лабораторные"
                    },
                    "color": "secondary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "payload": '{"button": "coursework"}',
                        "label": "📊 Курсовые"
                    },
                    "color": "secondary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "payload": '{"button": "diploma"}',
                        "label": "🎓 Дипломные"
                    },
                    "color": "secondary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "payload": '{"button": "other"}',
                        "label": "❔ Другое"
                    },
                    "color": "secondary"
                }
            ]
        ]
        return self.get_keyboard(buttons)

    def get_language_keyboard(self):
        """Меню выбора языка для VK"""
        buttons = [
            [
                {
                    "action": {
                        "type": "text",
                        "payload": '{"button": "cpp"}',
                        "label": "C++"
                    },
                    "color": "positive"
                },
                {
                    "action": {
                        "type": "text",
                        "payload": '{"button": "python"}',
                        "label": "Python"
                    },
                    "color": "positive"
                }
            ]
        ]
        return self.get_keyboard(buttons)

    def get_format_keyboard(self):
        """Меню формата обучения для VK"""
        buttons = [
            [
                {
                    "action": {
                        "type": "text",
                        "payload": '{"button": "individual"}',
                        "label": "👤 Онлайн индивидуально"
                    },
                    "color": "positive"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "payload": '{"button": "group"}',
                        "label": "👥 Онлайн в группе"
                    },
                    "color": "positive"
                }
            ]
        ]
        return self.get_keyboard(buttons)

    def send_message(self, user_id, message, keyboard=None):
        """Отправка сообщения в VK"""
        try:
            self.vk.messages.send(
                user_id=user_id,
                message=message,
                random_id=get_random_id(),
                keyboard=keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения в VK: {e}")

    def handle_start(self, user_id):
        """Обработка команды старт"""
        welcome_text = """
👋 Привет! Это Lab&Code.

Мы помогаем:
📚 Студентам — с лабораторными, курсовыми, дипломами
💻 Всем, кто хочет освоить C++ или Python

Что вас интересует?
        """
        self.send_message(user_id, welcome_text, self.get_main_keyboard())
        self.user_states[user_id] = "main_menu"

    def handle_student_help(self, user_id):
        """Обработка выбора помощи студентам"""
        self.send_message(user_id, "Какие работы нужны?", self.get_student_keyboard())
        self.user_states[user_id] = "student_help"

    def handle_programming_help(self, user_id):
        """Обработка выбора обучения программированию"""
        self.send_message(user_id, "Какой язык хотите изучать?", self.get_language_keyboard())
        self.user_states[user_id] = "programming_language"

    def handle_work_type(self, user_id, work_type):
        """Обработка выбора типа работы"""
        work_types = {
            "labs": "Лабораторные",
            "coursework": "Курсовые",
            "diploma": "Дипломные",
            "other": "Другое"
        }

        self.user_data[user_id] = {
            "category": "student_help",
            "work_type": work_types.get(work_type, "Другое"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.send_message(user_id, "Пожалуйста, оставьте свой номер телефона или ссылку на ваш профиль ВК для связи.")
        self.user_states[user_id] = "waiting_contact"

    def handle_language_choice(self, user_id, language):
        """Обработка выбора языка программирования"""
        language_name = "C++" if language == "cpp" else "Python"

        if user_id not in self.user_data:
            self.user_data[user_id] = {}

        self.user_data[user_id].update({
            "category": "programming",
            "language": language_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        self.send_message(user_id, "Выберите формат занятий:", self.get_format_keyboard())
        self.user_states[user_id] = "programming_format"

    def handle_format_choice(self, user_id, format_type):
        """Обработка выбора формата обучения"""
        format_name = "индивидуально" if format_type == "individual" else "в группе"

        if user_id in self.user_data:
            self.user_data[user_id]["format"] = format_name

        self.send_message(user_id, "Пожалуйста, оставьте свой номер телефона или ссылку на ваш профиль ВК для связи.")
        self.user_states[user_id] = "waiting_contact"

    def handle_contact_info(self, user_id, contact_info):
        """Обработка контактной информации"""
        if user_id in self.user_data:
            user_data = self.user_data[user_id]

            # Логируем запрос
            if user_data.get('category') == 'student_help':
                logger.info(f"📋 VK: Новый запрос от студента - {user_data.get('work_type')}, Контакт: {contact_info}")
            else:
                logger.info(
                    f"📋 VK: Новый запрос на обучение - {user_data.get('language')}, Формат: {user_data.get('format')}, Контакт: {contact_info}")

            # Отправляем уведомление админу
            notify_admin_vk(user_data, contact_info, user_id)

            # Отправляем подтверждение
            if user_data.get('category') == 'student_help':
                self.send_message(user_id, "✅ Спасибо! Мы свяжемся с вами в течение 15 минут.")
            else:
                self.send_message(user_id,
                                  "✅ Спасибо! Мы свяжемся с вами в течение 15 минут.\n\n🎁 Пока ждёте, можете скачать бонус: [ссылка на PDF]")

            # Планируем автосообщения
            asyncio.create_task(context.auto_message_scheduler.schedule_vk_messages(user_id, self))

            # Очищаем состояние
            self.user_states.pop(user_id, None)
            self.user_data.pop(user_id, None)

            # Возвращаем в главное меню
            self.send_message(user_id, "Хотите узнать что-то еще?", self.get_main_keyboard())

    async def run(self):
        """Запуск VK бота"""
        logger.info("🚀 Запуск VK бота Lab&Code...")

        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id = event.object.message['from_id']
                text = event.object.message['text']

                logger.info(f"VK сообщение от {user_id}: {text}")

                # Обработка команд
                if text.lower() in ['/start', 'начать', 'старт']:
                    self.handle_start(user_id)

                # Главное меню
                elif self.user_states.get(user_id) == "main_menu":
                    if "помощь студентам" in text.lower() or "1" in text:
                        self.handle_student_help(user_id)
                    elif "обучение программированию" in text.lower() or "2" in text:
                        self.handle_programming_help(user_id)

                # Помощь студентам
                elif self.user_states.get(user_id) == "student_help":
                    if "лабораторные" in text.lower() or "labs" in text:
                        self.handle_work_type(user_id, "labs")
                    elif "курсовые" in text.lower() or "coursework" in text:
                        self.handle_work_type(user_id, "coursework")
                    elif "дипломные" in text.lower() or "diploma" in text:
                        self.handle_work_type(user_id, "diploma")
                    elif "другое" in text.lower() or "other" in text:
                        self.handle_work_type(user_id, "other")

                # Выбор языка программирования
                elif self.user_states.get(user_id) == "programming_language":
                    if "c++" in text.lower() or "cpp" in text:
                        self.handle_language_choice(user_id, "cpp")
                    elif "python" in text.lower():
                        self.handle_language_choice(user_id, "python")

                # Выбор формата обучения
                elif self.user_states.get(user_id) == "programming_format":
                    if "индивидуально" in text.lower() or "individual" in text:
                        self.handle_format_choice(user_id, "individual")
                    elif "в группе" in text.lower() or "group" in text:
                        self.handle_format_choice(user_id, "group")

                # Ожидание контакта
                elif self.user_states.get(user_id) == "waiting_contact":
                    self.handle_contact_info(user_id, text)

                # Любое другое сообщение
                else:
                    self.handle_start(user_id)