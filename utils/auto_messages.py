# utils/auto_messages.py
import asyncio
import logging
from typing import Dict, List

# Логгер для автосообщений в том же формате
auto_message_logger = logging.getLogger('app')


class AutoMessageScheduler:
    def __init__(self, bot=None):
        self.bot = bot
        self.scheduled_tasks: Dict[int, List[asyncio.Task]] = {}
        auto_message_logger.info("AutoMessageScheduler инициализирован")

    def set_bot(self, bot):
        """Установка бота после инициализации"""
        self.bot = bot
        auto_message_logger.info("Бот установлен в AutoMessageScheduler")

    async def schedule_auto_messages(self, user_id: int):
        """Планирование автосообщений"""
        if self.bot is None:
            auto_message_logger.error("Бот не установлен в AutoMessageScheduler")
            return

        messages = [
            (10, "🔥 Полезно знать: 5 типичных ошибок студентов при написании кода."),
            (20, "📢 Отзыв: 'Lab&Code помог мне защитить диплом по Python!'"),
            (30, "⏳ Осталось 3 места на сентябрьский курс Python. Успей записаться!")
        ]

        for delay, text in messages:
            task = asyncio.create_task(
                self.send_auto_message(user_id, text, delay)
            )
            if user_id not in self.scheduled_tasks:
                self.scheduled_tasks[user_id] = []
            self.scheduled_tasks[user_id].append(task)

        auto_message_logger.info(f"Запланировано {len(messages)} автосообщений для пользователя {user_id}")

    async def send_auto_message(self, user_id: int, message: str, delay: int):
        """Отправка запланированного сообщения"""
        try:
            await asyncio.sleep(delay)
            await self.bot.send_message(user_id, message)
            auto_message_logger.info(f"Автосообщение отправлено пользователю {user_id}")
        except Exception as e:
            auto_message_logger.error(f"Ошибка отправки автосообщения пользователю {user_id}: {e}")

    def cancel_user_tasks(self, user_id: int):
        """Отмена задач для пользователя"""
        if user_id in self.scheduled_tasks:
            for task in self.scheduled_tasks[user_id]:
                task.cancel()
            del self.scheduled_tasks[user_id]
            auto_message_logger.info(f"Задачи отменены для пользователя {user_id}")