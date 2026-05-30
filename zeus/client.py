import os, sys
from telethon import TelegramClient
from telethon.sessions import StringSession

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_ID = int(os.environ.get("API_ID", "0") or "0")
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION_STRING", "")
BOT_NAME = os.environ.get("BOT_NAME", "GOJO Userbot")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
botClient = None
