from telethon import TelegramClient
from telethon.sessions import StringSession
import os, sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_ID_RAW = os.environ.get("API_ID", "")
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION_STRING", "")
BOT_NAME = os.environ.get("BOT_NAME", "GOJO Userbot")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

try:
    API_ID = int(API_ID_RAW) if API_ID_RAW else 0
except ValueError:
    API_ID = 0

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
botClient = None
