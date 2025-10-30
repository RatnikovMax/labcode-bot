# utils/logger.py
import logging
import os
from logging.handlers import TimedRotatingFileHandler
import glob
import time


class CustomFormatter(logging.Formatter):
    """Кастомный форматтер для единообразного вывода логов"""

    def format(self, record):
        # Сохраняем оригинальное сообщение
        original_message = record.getMessage()

        # Если это наше кастомное сообщение (не из aiogram), форматируем его
        if (not original_message.startswith('Update id=') and
                not original_message.startswith('Start polling') and
                not original_message.startswith('Run polling') and
                'aiogram' not in record.name):
            # Форматируем в стиле aiogram
            record.msg = f"{original_message}"

        return super().format(record)


def setup_logger():
    """Настройка логгера с ротацией раз в неделю"""

    # Создаем папку для логов если ее нет
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Основной форматтер
    formatter = CustomFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Основной логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Файловый обработчик с ротацией по понедельникам
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'bot.log'),
        when='W0',  # Ротация в понедельник
        interval=1,  # Каждую неделю
        backupCount=4,  # Хранить 4 файла (1 месяц)
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Очищаем старые обработчики и добавляем новые
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Настраиваем логгер для нашего приложения
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.INFO)
    app_logger.propagate = True  # Пропускаем логи в основной логгер

    logging.info("✅ Логгер настроен с ротацией раз в неделю")

    return logger


def cleanup_old_logs(log_dir="logs", days=30):
    """Очистка старых лог-файлов (старше 30 дней)"""
    try:
        current_time = time.time()

        for log_file in glob.glob(os.path.join(log_dir, "*.log*")):
            # Удаляем файлы старше days дней
            if os.path.getctime(log_file) < current_time - (days * 86400):
                os.remove(log_file)
                logging.info(f"🗑️ Удален старый лог-файл: {log_file}")

    except Exception as e:
        logging.error(f"❌ Ошибка при очистке логов: {e}")