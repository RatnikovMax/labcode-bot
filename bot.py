# bot.py
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers.start import router as start_router
from handlers.student_help import router as student_router
from handlers.programming import router as programming_router
from handlers.common import router as common_router
from utils.auto_messages import AutoMessageScheduler
from utils.context import set_bot, set_scheduler
from utils.logger import setup_logger, cleanup_old_logs

# Настройка логгера
setup_logger()
cleanup_old_logs()

logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
auto_message_scheduler = AutoMessageScheduler()
auto_message_scheduler.set_bot(bot)

# Устанавливаем глобальные объекты
set_bot(bot)
set_scheduler(auto_message_scheduler)

# Регистрация роутеров
dp.include_router(start_router)
dp.include_router(student_router)
dp.include_router(programming_router)
dp.include_router(common_router)


async def main():
    logger.info("🚀 Запуск бота Lab&Code в Docker...")

    # Информация о среде выполнения (для отладки)
    logger.info(f"Python version: {os.sys.version}")
    logger.info(f"Running in container: {os.path.exists('/.dockerenv')}")

    # Отправляем сообщение админу о запуске бота
    from config import ADMIN_ID
    if ADMIN_ID:
        try:
            await bot.send_message(
                ADMIN_ID,
                "🐳 Бот Lab&Code запущен в Docker и готов к работе!",
                parse_mode='Markdown'
            )
            logger.info("✅ Уведомление о запуске отправлено админу")
        except Exception as e:
            logger.error(f"❌ Не удалось отправить уведомление о запуске: {e}")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
        raise
    finally:
        # Корректное завершение работы
        for user_tasks in auto_message_scheduler.scheduled_tasks.values():
            for task in user_tasks:
                task.cancel()
        await bot.session.close()
        logger.info("⏹ Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹ Бот остановлен по команде пользователя")
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка: {e}")
        exit(1)