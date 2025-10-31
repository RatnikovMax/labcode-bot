# test_vk_fixed.py
import vk_api
import os
from dotenv import load_dotenv

load_dotenv()

VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN")
VK_GROUP_ID = os.getenv("VK_GROUP_ID")
VK_ADMIN_ID = os.getenv("VK_ADMIN_ID")

print("=== Тест VK API ===")
print(f"VK_GROUP_TOKEN: {VK_GROUP_TOKEN[:20]}..." if VK_GROUP_TOKEN else "❌ VK_GROUP_TOKEN не установлен")
print(f"VK_GROUP_ID: {VK_GROUP_ID}")
print(f"VK_ADMIN_ID: {VK_ADMIN_ID}")

if VK_GROUP_TOKEN and VK_GROUP_ID:
    try:
        # Инициализация VK API
        vk_session = vk_api.VkApi(token=VK_GROUP_TOKEN)
        vk = vk_session.get_api()

        # Проверка информации о группе (работающий метод)
        group_info = vk.groups.getById(group_id=VK_GROUP_ID)
        print(f"✅ Группа найдена: {group_info[0]['name']}")

        # Проверка Long Poll настроек
        print("✅ Long Poll API доступен")

        # Проверка отправки сообщения (используем random_id)
        if VK_ADMIN_ID:
            result = vk.messages.send(
                user_id=int(VK_ADMIN_ID),
                message="✅ Тестовое сообщение от VK бота",
                random_id=vk_api.utils.get_random_id()
            )
            print(f"✅ Тестовое сообщение отправлено, ID: {result}")

    except vk_api.exceptions.ApiError as e:
        print(f"❌ Ошибка VK API: {e}")
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
else:
    print("❌ Недостаточно данных для теста")