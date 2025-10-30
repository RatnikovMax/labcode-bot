# run.py
import asyncio
import logging
from bot import main as telegram_main
from vk_bot import VKBot
from utils.logger import setup_logger


async def run_all_bots():
    """Запуск всех ботов"""
    setup_logger()
    logger = logging.getLogger(__name__)

    logger.info("🚀 Запуск мульти-платформенного бота Lab&Code...")

    try:
        # Запускаем Telegram бота в отдельной задаче
        telegram_task = asyncio.create_task(telegram_main())

        # Запускаем VK бота (если настроен)
        from config import VK_GROUP_TOKEN
        if VK_GROUP_TOKEN:
            vk_bot = VKBot()
            vk_task = asyncio.create_task(vk_bot.run())
            await asyncio.gather(telegram_task, vk_task)
        else:
            await telegram_task

    except Exception as e:
        logger.error(f"❌ Ошибка при запуске ботов: {e}")


if __name__ == "__main__":
    asyncio.run(run_all_bots())