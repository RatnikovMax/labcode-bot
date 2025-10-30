# Dockerfile
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для безопасности
RUN useradd -m -u 1000 botuser

# Создание рабочей директории
WORKDIR /app

# Копирование requirements сначала для кэширования
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание папки для логов
RUN mkdir -p /app/logs && chown botuser:botuser /app/logs

# Смена пользователя
USER botuser

# Скрипт запуска
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]