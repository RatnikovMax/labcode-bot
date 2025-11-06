# vk_bot.py
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import logging
import json
import time
import requests
from datetime import datetime

from config import VK_GROUP_TOKEN, VK_GROUP_ID, VK_ADMIN_ID
from utils.auto_messages import AutoMessageScheduler
from utils.notifications import notify_admin_vk

logger = logging.getLogger(__name__)


class VKBot:
    def __init__(self):
        self.max_retries = 10  # Увеличиваем количество попыток
        self.retry_delay = 30  # секунд
        self.running = True
        self._init_session()

    def _init_session(self):
        """Инициализация VK сессии с обработкой ошибок"""
        try:
            logger.info("🔄 Создание VK сессии...")
            # Добавляем таймауты и повторные попытки
            session = requests.Session()
            session.timeout = 30
            self.vk_session = vk_api.VkApi(
                token=VK_GROUP_TOKEN,
                session=session,
                api_version='5.131'
            )
            logger.info("🔄 Инициализация LongPoll...")
            # Увеличиваем таймаут LongPoll
            self.longpoll = VkBotLongPoll(
                self.vk_session,
                int(VK_GROUP_ID),
                wait=25
            )
            logger.info("🔄 Получение VK API...")
            self.vk = self.vk_session.get_api()
            self.user_states = {}
            self.user_data = {}
            self.auto_message_scheduler = AutoMessageScheduler()
            logger.info("✅ VK бот инициализирован")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации VK бота: {e}", exc_info=True)
            return False

    def _test_connection(self):
        """Проверка соединения с VK API"""
        try:
            # Проверяем доступность VK API
            response = requests.get(
                'https://api.vk.com/method/utils.getServerTime',
                timeout=10
            )
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'response' in data:
                        logger.info("✅ Соединение с VK API установлено")
                        return True
                    else:
                        logger.warning("⚠️ VK API вернул неожиданный ответ")
                        return False
                except json.JSONDecodeError:
                    logger.warning("⚠️ VK API вернул не JSON ответ")
                    return False
            else:
                logger.warning(f"⚠️ VK API недоступен, статус: {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Проблемы с соединением VK API: {e}")
            return False

    def _reconnect(self):
        """Переподключение к VK API"""
        logger.info("🔄 Попытка переподключения к VK...")
        time.sleep(self.retry_delay)
        return self._init_session()

    def _safe_longpoll_listen(self):
        """Безопасное прослушивание LongPoll с обработкой JSON ошибок"""
        try:
            for event in self.longpoll.listen():
                yield event
        except (json.JSONDecodeError, requests.exceptions.JSONDecodeError) as e:
            logger.error(f"❌ Ошибка парсинга JSON от VK: {e}")
            raise ConnectionError("JSON parse error") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Сетевая ошибка VK: {e}")
            raise ConnectionError("Network error") from e
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка LongPoll: {e}")
            raise

    def get_keyboard(self, keyboard_type="main_menu"):
        """Создание клавиатур для VK"""
        keyboard = VkKeyboard(one_time=True)

        if keyboard_type == "main_menu":
            keyboard.add_button("🎓 Помощь студентам", color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()
            keyboard.add_button("💻 Обучение программированию", color=VkKeyboardColor.SECONDARY)

        elif keyboard_type == "student_help":
            keyboard.add_button("📝 Лабораторные", color=VkKeyboardColor.PRIMARY)
            keyboard.add_button("📊 Курсовые", color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()
            keyboard.add_button("🎓 Дипломные", color=VkKeyboardColor.PRIMARY)
            keyboard.add_button("❔ Другое", color=VkKeyboardColor.SECONDARY)
            keyboard.add_line()
            keyboard.add_button("⬅️ Назад", color=VkKeyboardColor.NEGATIVE)

        elif keyboard_type == "programming":
            keyboard.add_button("C++", color=VkKeyboardColor.PRIMARY)
            keyboard.add_button("Python", color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()
            keyboard.add_button("⬅️ Назад", color=VkKeyboardColor.NEGATIVE)

        elif keyboard_type == "format":
            keyboard.add_button("👤 Индивидуально", color=VkKeyboardColor.PRIMARY)
            keyboard.add_button("👥 В группе", color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()
            keyboard.add_button("⬅️ Назад", color=VkKeyboardColor.NEGATIVE)

        elif keyboard_type == "back_only":
            keyboard.add_button("⬅️ Назад", color=VkKeyboardColor.NEGATIVE)

        return keyboard.get_keyboard()

    def send_message(self, user_id, message, keyboard=None):
        """Отправка сообщения пользователю"""
        try:
            params = {
                'user_id': user_id,
                'message': message,
                'random_id': get_random_id(),
            }
            if keyboard:
                params['keyboard'] = keyboard

            self.vk.messages.send(**params)
            logger.info(f"✅ Сообщение отправлено пользователю {user_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения: {e}")

    def handle_start(self, user_id):
        """Обработка команды старт"""
        welcome_message = (
            "👋 Добро пожаловать в Lab&Code!\n\n"
            "Я помогу вам:\n"
            "• 🎓 С учебными работами (лабораторные, курсовые, дипломные)\n"
            "• 💻 Освоить программирование (C++, Python)\n\n"
            "Выберите направление:"
        )

        self.user_states[user_id] = "main_menu"
        self.send_message(user_id, welcome_message, self.get_keyboard("main_menu"))

    def handle_student_help(self, user_id):
        """Обработка раздела помощи студентам"""
        message = (
            "🎓 Помощь студентам\n\n"
            "Выберите тип работы:\n"
            "• 📝 Лабораторные работы\n"
            "• 📊 Курсовые работы\n"
            "• 🎓 Дипломные работы\n"
            "• ❔ Другие учебные работы"
        )

        self.user_states[user_id] = "student_help"
        self.user_data[user_id] = {"category": "student_help"}
        self.send_message(user_id, message, self.get_keyboard("student_help"))

    def handle_programming_help(self, user_id):
        """Обработка раздела обучения программированию"""
        message = (
            "💻 Обучение программированию\n\n"
            "Выберите язык программирования:\n"
            "• C++ - для системного программирования\n"
            "• Python - для веб-разработки и анализа данных"
        )

        self.user_states[user_id] = "programming_language"
        self.user_data[user_id] = {"category": "programming"}
        self.send_message(user_id, message, self.get_keyboard("programming"))

    def handle_work_type(self, user_id, work_type):
        """Обработка выбора типа работы"""
        work_types = {
            "лабораторные": "📝 Лабораторные работы",
            "курсовые": "📊 Курсовые работы",
            "дипломные": "🎓 Дипломные работы",
            "другое": "❔ Другие учебные работы"
        }

        message = (
            f"{work_types[work_type]}\n\n"
            "📞 Для обсуждения деталей и расчета стоимости, "
            "пожалуйста, оставьте ваш контакт (телеgram, email или номер телефона):"
        )

        self.user_states[user_id] = "waiting_contact"
        self.user_data[user_id]["work_type"] = work_type
        self.send_message(user_id, message, self.get_keyboard("back_only"))

    def handle_language_choice(self, user_id, language):
        """Обработка выбора языка программирования"""
        languages = {
            "c++": "C++",
            "python": "Python"
        }

        message = (
            f"💻 {languages[language]}\n\n"
            "Выберите формат обучения:\n"
            "• 👤 Индивидуально - персональные занятия\n"
            "• 👥 В группе - занятия в мини-группах"
        )

        self.user_states[user_id] = "programming_format"
        self.user_data[user_id]["language"] = language
        self.send_message(user_id, message, self.get_keyboard("format"))

    def handle_format_choice(self, user_id, format_type):
        """Обработка выбора формата обучения"""
        message = (
            f"👤 {format_type.capitalize()}\n\n"
            "📞 Для обсуждения деталей и стоимости занятий, "
            "пожалуйста, оставьте ваш контакт (telegram, email или номер телефона):"
        )

        self.user_states[user_id] = "waiting_contact"
        self.user_data[user_id]["format"] = format_type
        self.send_message(user_id, message, self.get_keyboard("back_only"))

    def handle_back(self, user_id):
        """Обработка возврата назад"""
        current_state = self.user_states.get(user_id, "main_menu")

        if current_state == "student_help":
            self.handle_start(user_id)
        elif current_state == "programming_language":
            self.handle_start(user_id)
        elif current_state == "programming_format":
            self.handle_programming_help(user_id)
        elif current_state == "waiting_contact":
            if self.user_data.get(user_id, {}).get("category") == "student_help":
                self.handle_student_help(user_id)
            else:
                self.handle_programming_help(user_id)
        else:
            self.handle_start(user_id)

    def handle_contact_info(self, user_id, contact_info):
        """Обработка контактной информации"""
        user_data = self.user_data.get(user_id, {})

        # Формируем уведомление для админа
        notification = f"📞 Новый запрос от пользователя VK ID: {user_id}\n"

        if user_data.get("category") == "student_help":
            work_type = user_data.get("work_type", "не указан")
            notification += f"🎓 Тип работы: {work_type}\n"
        else:
            language = user_data.get("language", "не указан")
            format_type = user_data.get("format", "не указан")
            notification += f"💻 Язык: {language}\n"
            notification += f"👤 Формат: {format_type}\n"

        notification += f"📱 Контакт: {contact_info}\n"
        notification += f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # Отправляем уведомление админу
        try:
            from utils.notifications import notify_admin_vk
            notify_admin_vk(user_data, contact_info, user_id)
            logger.info(f"✅ Уведомление отправлено админу о контакте от {user_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки уведомления админу: {e}")

        # Благодарность пользователю
        thank_message = (
            "✅ Спасибо! Ваша заявка принята.\n\n"
            "📞 Мы свяжемся с вами в ближайшее время для уточнения деталей.\n\n"
            "Если у вас есть срочный вопрос, напишите нам напрямую."
        )

        self.user_states[user_id] = "main_menu"
        self.send_message(user_id, thank_message, self.get_keyboard("main_menu"))

    def run(self):
        """Запуск VK бота с улучшенным переподключением"""
        logger.info("🚀 VK бот запущен, ожидаем сообщения...")

        retry_count = 0

        while self.running and retry_count < self.max_retries:
            try:
                # Проверяем подключение
                if not self._test_connection():
                    logger.warning("⚠️ Проблемы с интернет-соединением")
                    time.sleep(10)
                    continue

                # Проверяем подключение к группе
                try:
                    group_info = self.vk.groups.getById(group_id=int(VK_GROUP_ID))
                    logger.info(f"✅ Подключение к группе: {group_info[0]['name']}")
                except Exception as e:
                    logger.error(f"❌ Ошибка подключения к группе: {e}")
                    retry_count += 1
                    if retry_count < self.max_retries:
                        logger.info(f"🔄 Переподключение через {self.retry_delay} секунд...")
                        time.sleep(self.retry_delay)
                        if not self._reconnect():
                            logger.error("❌ Не удалось переподключиться")
                        continue
                    else:
                        break

                # Сбрасываем счетчик повторных попыток при успешном подключении
                retry_count = 0

                # Основной цикл обработки событий
                for event in self._safe_longpoll_listen():
                    if not self.running:
                        break

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
                                self.send_message(user_id, "Выберите формат занятий:", self.get_keyboard("format"))

                        # Ожидание контакта
                        elif current_state == "waiting_contact":
                            self.handle_contact_info(user_id, text)

                        # Возврат в главное меню
                        elif "в главное меню" in text or "🏠" in text:
                            self.handle_start(user_id)

                        # Любое другое сообщение
                        else:
                            self.handle_start(user_id)

            except (ConnectionError, requests.exceptions.RequestException) as e:
                retry_count += 1
                logger.error(f"❌ Сетевая ошибка VK (попытка {retry_count}/{self.max_retries}): {e}")
                if retry_count < self.max_retries:
                    logger.info(f"🔄 Переподключение через {self.retry_delay} секунд...")
                    if not self._reconnect():
                        logger.error("❌ Не удалось переподключиться")
                else:
                    logger.error("❌ Достигнут лимит попыток переподключения. VK бот остановлен.")
                    break

            except Exception as e:
                retry_count += 1
                logger.error(f"❌ Неожиданная ошибка VK бота (попытка {retry_count}/{self.max_retries}): {e}", exc_info=True)
                if retry_count < self.max_retries:
                    logger.info(f"🔄 Перезапуск через {self.retry_delay} секунд...")
                    time.sleep(self.retry_delay)
                    if not self._reconnect():
                        logger.error("❌ Не удалось переподключиться")
                else:
                    logger.error("❌ Достигнут лимит попыток переподключения. VK бот остановлен.")
                    break

        logger.error("❌ VK бот завершил работу из-за множественных ошибок")

    def stop(self):
        """Остановка бота"""
        logger.info("⏹️ Остановка VK бота...")
        self.running = False