# run.py
import asyncio
import logging
import threading
from bot import main as telegram_main
from vk_bot import VKBot
from utils.logger import setup_logger
from config import VK_GROUP_TOKEN, VK_GROUP_ID


async def run_telegram_bot():
    """Запуск Telegram бота"""
    try:
        await telegram_main()
    except Exception as e:
        logging.error(f"❌ Ошибка в Telegram боте: {e}")


def run_vk_bot():
    """Запуск VK бота в отдельном потоке"""
    try:
        vk_bot = VKBot()
        vk_bot.run()
    except Exception as e:
        logging.error(f"❌ Ошибка в VK боте: {e}")


async def main():
    """Главная функция запуска"""
    setup_logger()
    logger = logging.getLogger(__name__)

    logger.info("🚀 Запуск мульти-платформенного бота Lab&Code...")

    # Отладочная информация
    logger.info(f"VK_GROUP_TOKEN: {'✅ Установлен' if VK_GROUP_TOKEN else '❌ Отсутствует'}")
    logger.info(f"VK_GROUP_ID: {VK_GROUP_ID}")

    # Запускаем VK бота в отдельном потоке (если настроен)
    if VK_GROUP_TOKEN and VK_GROUP_ID:
        logger.info("✅ Запуск VK бота в отдельном потоке...")
        vk_thread = threading.Thread(target=run_vk_bot, daemon=True)
        vk_thread.start()
    else:
        logger.info("❌ VK бот отключен - проверьте настройки")

    # Запускаем Telegram бота в основном потоке
    await run_telegram_bot()


if __name__ == "__main__":
    asyncio.run(main())