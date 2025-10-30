# utils/logger.py
import logging
import os
from logging.handlers import TimedRotatingFileHandler
import glob
import tempfile

def setup_logger():
    """Настройка логгера с записью во временную директорию"""

    # Используем временную директорию
    log_dir = tempfile.gettempdir()

    # Основной форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Основной логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Файловый обработчик во временную директорию
    log_file = os.path.join(log_dir, 'bot.log')
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when='W0',
        interval=1,
        backupCount=4,
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

    logging.info(f"✅ Логгер настроен. Логи в: {log_file}")

    return logger

def cleanup_old_logs():
    """Очистка старых лог-файлов (заглушка)"""
    pass