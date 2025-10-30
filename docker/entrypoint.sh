#!/bin/bash
# docker/entrypoint.sh

echo "🚀 Запуск Lab&Code Telegram Bot..."

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "Пожалуйста, создайте .env файл с переменными BOT_TOKEN и ADMIN_ID"
    exit 1
fi

# Проверка обязательных переменных
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN не установлен!"
    exit 1
fi

echo "✅ Все проверки пройдены"
echo "🤖 Запуск бота..."

# Запуск бота
exec python bot.py