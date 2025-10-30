#!/usr/bin/env python3
# monitor.py
import psutil
import logging
import os
from datetime import datetime


def check_bot_status():
    """Проверка состояния бота"""
    bot_running = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and 'run.py' in ' '.join(proc.info['cmdline']):
                bot_running = True
                print(f"✅ Бот запущен (PID: {proc.info['pid']})")
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if not bot_running:
        print("❌ Бот не запущен")

    # Проверка использования памяти
    memory = psutil.virtual_memory()
    print(f"💾 Использование памяти: {memory.percent}%")

    # Проверка диска
    disk = psutil.disk_usage('/')
    print(f"💿 Свободно на диске: {disk.free // (1024 ** 3)}GB")


if __name__ == "__main__":
    check_bot_status()