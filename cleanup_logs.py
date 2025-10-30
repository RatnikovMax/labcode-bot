# cleanup_logs.py
"""
Скрипт для очистки старых лог-файлов
Запускайте раз в неделю через cron или планировщик задач
"""

import os
import glob
import time
from datetime import datetime


def cleanup_logs(log_dir="logs", keep_days=30):
    """Очистка лог-файлов старше keep_days дней"""

    if not os.path.exists(log_dir):
        print(f"📁 Папка {log_dir} не существует")
        return

    current_time = time.time()
    deleted_count = 0

    # Ищем все лог-файлы
    for log_file in glob.glob(os.path.join(log_dir, "*.log*")):
        file_time = os.path.getctime(log_file)

        # Если файл старше keep_days дней
        if file_time < current_time - (keep_days * 86400):
            try:
                os.remove(log_file)
                deleted_count += 1
                print(f"🗑️ Удален: {log_file}")
            except Exception as e:
                print(f"❌ Ошибка удаления {log_file}: {e}")

    print(f"✅ Очистка завершена. Удалено файлов: {deleted_count}")


if __name__ == "__main__":
    print(f"🕐 Начало очистки логов: {datetime.now()}")
    cleanup_logs()