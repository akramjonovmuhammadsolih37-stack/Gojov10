"""
SESSION_STRING olish uchun bu faylni bir marta ishga tushiring:
  python get_session.py

Keyin chiqgan SESSION_STRING ni Render'da environment variable ga qo'ying.
"""
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

print("=" * 50)
print("  GOJO-USERBOT — Session String Generator")
print("=" * 50)

API_ID = int(input("\nAPI_ID kiriting: "))
API_HASH = input("API_HASH kiriting: ").strip()

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    session = client.session.save()

print("\n" + "=" * 50)
print("SESSION_STRING:")
print(session)
print("=" * 50)
print("\nYuqoridagi SESSION_STRING ni Render > Environment ga qo'ying!")
