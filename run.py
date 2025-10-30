import os
import sys
import asyncio
from bot import main

if __name__ == "__main__":
    # Проверяем наличие .env файла
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("Скопируйте .env.example в .env и настройте переменные")
        sys.exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        sys.exit(1)