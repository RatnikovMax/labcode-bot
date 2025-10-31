import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")

# VK переменные
VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN")
VK_GROUP_ID = os.getenv("VK_GROUP_ID")
VK_ADMIN_ID = os.getenv("VK_ADMIN_ID")

# Приведение типов
if VK_GROUP_ID:
    try:
        VK_GROUP_ID = int(VK_GROUP_ID)
    except (ValueError, TypeError):
        print("❌ VK_GROUP_ID должен быть числом")
        VK_GROUP_ID = None

if VK_ADMIN_ID:
    try:
        VK_ADMIN_ID = int(VK_ADMIN_ID)
    except (ValueError, TypeError):
        print("❌ VK_ADMIN_ID должен быть числом")
        VK_ADMIN_ID = None

if not VK_GROUP_TOKEN:
    print("⚠️  VK_GROUP_TOKEN не найден. VK бот отключен")