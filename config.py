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

if not VK_GROUP_TOKEN:
    print("⚠️  VK_GROUP_TOKEN не найден. VK бот отключен")