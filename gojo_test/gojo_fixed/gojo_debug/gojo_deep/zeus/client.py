from telethon import TelegramClient
from telethon.sessions import StringSession
import os, sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_missing = []

_api_id_raw = os.environ.get("API_ID", "")
if not _api_id_raw:
    _missing.append("API_ID")

_api_hash = os.environ.get("API_HASH", "")
if not _api_hash:
    _missing.append("API_HASH")

SESSION = os.environ.get("SESSION_STRING", "")
if not SESSION:
    _missing.append("SESSION_STRING")

if _missing:
    print("[ERROR] Quyidagi o'zgaruvchilar topilmadi:")
    for m in _missing:
        print(f"  ✗  {m}")
    print()
    print("[INFO] Render Dashboard > Environment Variables ga qo'shing")
    sys.exit(1)

try:
    API_ID = int(_api_id_raw)
except ValueError:
    print(f"[ERROR] API_ID son bo'lishi kerak: '{_api_id_raw}'")
    sys.exit(1)

API_HASH = _api_hash
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BOT_NAME = os.environ.get("BOT_NAME", "GOJO Userbot")

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# botClient — faqat BOT_TOKEN berilganda, main() ichida ishga tushiriladi
botClient = None
