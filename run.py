# run.py (обновленная версия)
import asyncio
import logging
import threading
import time
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
    """Запуск VK бота в отдельном потоке с обработкой ошибок"""
    max_restarts = 10
    restart_count = 0
    base_delay = 10

    while restart_count < max_restarts:
        try:
            logging.info(f"🔄 Попытка запуска VK бота #{restart_count + 1}")
            vk_bot = VKBot()
            vk_bot.run_with_retry(max_retries=5, base_delay=5)

        except Exception as e:
            restart_count += 1
            logging.error(f"❌ VK бот упал (попытка {restart_count}/{max_restarts}): {e}")

            if restart_count < max_restarts:
                delay = min(base_delay * (2 ** (restart_count - 1)), 300)  # Максимум 5 минут
                logging.info(f"⏳ Перезапуск VK бота через {delay} секунд...")
                time.sleep(delay)
            else:
                logging.error("💥 Превышено максимальное количество перезапусков VK бота")
                break


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
        logger.info(f"✅ VK поток запущен. ID: {vk_thread.ident}, Alive: {vk_thread.is_alive()}")
    else:
        logger.info("❌ VK бот отключен - проверьте настройки")

    # Запускаем Telegram бота в основном потоке
    logger.info("✅ Запуск Telegram бота...")
    await run_telegram_bot()


if __name__ == "__main__":
    asyncio.run(main())