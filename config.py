import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8357063170:AAEpJHkulArjRUWFzMLVFA5yxeDrrX4CpwI")
ADMIN_ID = os.getenv("1121138765")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")

VK_GROUP_TOKEN = os.getenv("vk1.a.y04ThTBkB2pti_hrrYgTYcVQ1n1XcmVD49GW0YJD6TMJEwxnTdiWC87NWI92g7p1KIaA3FMFulgBeaHxP5Mc3LdckEfD5v3iRg2lHvKD_NcVF-dAa7Bz9CG9TnHH8H6RwQs_bgOTJO0oAuMpuEefjrwqRdXJYAdJTFDWXhTWeX-IPWb6hr8DnRChISxABKK0E3Jb92uiud7x9STKYnHS9w")
VK_GROUP_ID = os.getenv("232456723")
VK_ADMIN_ID = os.getenv("370638795")

if not VK_GROUP_TOKEN:
    print("⚠️  VK_GROUP_TOKEN не найден. VK бот отключен")