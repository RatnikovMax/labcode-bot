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
            self.vk_session = vk_api.VkApi(token=VK_GROUP_TOKEN)
            self.longpoll = VkBotLongPoll(self.vk_session, VK_GROUP_ID)
            self.vk = self.vk_session.get_api()
            self.user_states = {}
            self.user_data = {}
            self.auto_message_scheduler = AutoMessageScheduler()
            logger.info("✅ VK бот инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации VK бота: {e}")
            raise

    def get_keyboard(self, buttons, one_time=False):
        """Создание клавиатуры для VK"""
        keyboard = {
            "one_time": one_time,
            "buttons": buttons
        }
        return json.dumps(keyboard, ensure_ascii=False)

    def get_main_keyboard(self):
        """Главное меню для VK"""
        buttons = [
            [{
                "action": {
                    "type": "text",
                    "label": "🎓 Помощь студентам"
                },
                "color": "primary"
            }],
            [{
                "action": {
                    "type": "text",
                    "label": "💻 Обучение программированию"
                },
                "color": "primary"
            }]
        ]
        return self.get_keyboard(buttons, one_time=True)

    def get_student_keyboard(self):
        """Меню помощи студентам для VK"""
        buttons = [
            [{
                "action": {
                    "type": "text",
                    "label": "📝 Лабораторные"
                },
                "color": "secondary"
            }],
            [{
                "action": {
                    "type": "text",
                    "label": "📊 Курсовые"
                },
                "color": "secondary"
            }],
            [{
                "action": {
                    "type": "text",
                    "label": "🎓 Дипломные"
                },
                "color": "secondary"
            }],
            [{
                "action": {
                    "type": "text",
                    "label": "❔ Другое"
                },
                "color": "secondary"
            }],
            [{
                "action": {
                    "type": "text",
                    "label": "⬅️ Назад"
                },
                "color": "negative"
            }]
        ]
        return self.get_keyboard(buttons, one_time=True)

    def get_language_keyboard(self):
        """Меню выбора языка для VK"""
        buttons = [
            [{
                "action": {
                    "type": "text",
                    "label": "C++"
                },
                "color": "positive"
            },
                {
                    "action": {
                        "type": "text",
                        "label": "Python"
                    },
                    "color": "positive"
                }],
            [{
                "action": {
                    "type": "text",
                    "label": "⬅️ Назад"
                },
                "color": "negative"
            }]
        ]
        return self.get_keyboard(buttons, one_time=True)

    def get_format_keyboard(self):
        """Меню формата обучения для VK"""
        buttons = [
            [{
                "action": {
                    "type": "text",
                    "label": "👤 Онлайн индивидуально"
                },
                "color": "positive"
            }],
            [{
                "action": {
                    "type": "text",
                    "label": "👥 Онлайн в группе"
                },
                "color": "positive"
            }],
            [{
                "action": {
                    "type": "text",
                    "label": "⬅️ Назад"
                },
                "color": "negative"
            }]
        ]
        return self.get_keyboard(buttons, one_time=True)

    def get_main_menu_button(self):
        """Кнопка возврата в главное меню"""
        buttons = [
            [{
                "action": {
                    "type": "text",
                    "label": "🏠 В главное меню"
                },
                "color": "primary"
            }]
        ]
        return self.get_keyboard(buttons, one_time=True)

    def send_message(self, user_id, message, keyboard=None):
        """Отправка сообщения в VK"""
        try:
            self.vk.messages.send(
                user_id=user_id,
                message=message,
                random_id=get_random_id(),
                keyboard=keyboard
            )
            logger.info(f"✅ Сообщение отправлено пользователю VK {user_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения в VK: {e}")

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
            "лабораторные": "Лабораторные",
            "курсовые": "Курсовые",
            "дипломные": "Дипломные",
            "другое": "Другое"
        }

        self.user_data[user_id] = {
            "category": "student_help",
            "work_type": work_types.get(work_type, "Другое"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id
        }

        self.send_message(user_id, "Пожалуйста, оставьте свой номер телефона или ссылку на ваш профиль ВК для связи.")
        self.user_states[user_id] = "waiting_contact"

    def handle_language_choice(self, user_id, language):
        """Обработка выбора языка программирования"""
        language_name = "C++" if language.lower() == "c++" else "Python"

        self.user_data[user_id] = {
            "category": "programming",
            "language": language_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id
        }

        self.send_message(user_id, "Выберите формат занятий:", self.get_format_keyboard())
        self.user_states[user_id] = "programming_format"

    def handle_format_choice(self, user_id, format_type):
        """Обработка выбора формата обучения"""
        format_name = "индивидуально" if "индивидуально" in format_type.lower() else "в группе"

        if user_id in self.user_data:
            self.user_data[user_id]["format"] = format_name

        self.send_message(user_id, "Пожалуйста, оставьте свой номер телефона или ссылку на ваш профиль ВК для связи.")
        self.user_states[user_id] = "waiting_contact"

    def handle_contact_info(self, user_id, contact_info):
        """Обработка контактной информации"""
        if user_id in self.user_data:
            user_data = self.user_data[user_id]
            user_data["contact"] = contact_info

            # Логируем запрос
            if user_data.get('category') == 'student_help':
                logger.info(f"📋 VK: Новый запрос от студента:\n"
                            f"👤 Пользователь: VK ID: {user_id}\n"
                            f"📝 Тип работы: {user_data.get('work_type')}\n"
                            f"📞 Контакт: {contact_info}\n"
                            f"{'=' * 50}")
            else:
                logger.info(f"📋 VK: Новый запрос на обучение:\n"
                            f"👤 Пользователь: VK ID: {user_id}\n"
                            f"💻 Язык: {user_data.get('language')}\n"
                            f"📚 Формат: {user_data.get('format')}\n"
                            f"📞 Контакт: {contact_info}\n"
                            f"{'=' * 50}")

            # Отправляем уведомление админу
            notify_admin_vk(user_data, contact_info, user_id)

            # Отправляем подтверждение
            if user_data.get('category') == 'student_help':
                self.send_message(user_id, "✅ Спасибо! Мы свяжемся с вами в течение 15 минут.",
                                  self.get_main_menu_button())
            else:
                self.send_message(user_id,
                                  "✅ Спасибо! Мы свяжемся с вами в течение 15 минут.\n\n🎁 Пока ждёте, можете скачать бонус: [ссылка на PDF]",
                                  self.get_main_menu_button())

            # Планируем автосообщения
            asyncio.create_task(self.auto_message_scheduler.schedule_vk_messages(user_id, self))

            # Очищаем состояние
            self.user_states.pop(user_id, None)
            self.user_data.pop(user_id, None)

    def handle_back(self, user_id):
        """Обработка кнопки назад"""
        self.handle_start(user_id)

    def run(self):
        """Запуск VK бота"""
        logger.info("🚀 VK бот запущен, ожидаем сообщения...")

        try:
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
            logger.error(f"❌ Ошибка в VK боте: {e}")