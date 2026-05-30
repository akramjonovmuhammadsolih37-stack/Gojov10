#!/usr/bin/env python3
import sys, os, importlib, glob, asyncio
sys.stdout.reconfigure(line_buffering=True)

try:
    from keep_alive import keep_alive
    keep_alive()
    print("[OK] Keep-alive ishga tushdi!")
except Exception as e:
    print(f"[INFO] Keep-alive: {e}")

from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION_STRING", "")

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

SKIP_FILES = {"client.py", "__init__.py", "magic.py", "emojify.py"}
base_dir = os.path.dirname(os.path.abspath(__file__))
plugin_files = sorted(glob.glob(os.path.join(base_dir, "zeus", "*.py")))

loaded = []
failed = []

for filepath in plugin_files:
    filename = os.path.basename(filepath)
    if filename in SKIP_FILES:
        continue
    module_name = f"zeus.{filename[:-3]}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        module.client = client
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        count = 0
        for attr_name in vars(module):
            obj = getattr(module, attr_name)
            if callable(obj) and hasattr(obj, "_events"):
                for ev in obj._events:
                    client.add_event_handler(obj, ev)
                    count += 1
        loaded.append(filename)
        print(f"[OK] {filename} ({count} handler)")
    except Exception as e:
        import traceback
        failed.append(filename)
        print(f"[XATO] {filename}: {e}")
        traceback.print_exc()

print(f"\n[INFO] {len(loaded)} plugin, {len(failed)} xato")
print("[OK] GOJO tayyor!\n")

async def startup_animation():
    me = await client.get_me()
    username = f"@{me.username}" if me.username else str(me.id)
    bot_name = os.environ.get("BOT_NAME", "GOJO Userbot")
    frames = ["⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛","🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛","🟦🟦⬛⬛⬛⬛⬛⬛⬛⬛","🟦🟦🟦⬛⬛⬛⬛⬛⬛⬛","🟦🟦🟦🟦⬛⬛⬛⬛⬛⬛","🟦🟦🟦🟦🟦⬛⬛⬛⬛⬛","🟦🟦🟦🟦🟦🟦⬛⬛⬛⬛","🟦🟦🟦🟦🟦🟦🟦⬛⬛⬛","🟦🟦🟦🟦🟦🟦🟦🟦⬛⬛","🟦🟦🟦🟦🟦🟦🟦🟦🟦⬛","🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦"]
    msg = await client.send_message("me", "⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛\n`Yuklanmoqda...`")
    for frame in frames:
        await asyncio.sleep(0.35)
        await msg.edit(f"{frame}\n`Yuklanmoqda...`")
    for neon in ["⚡️⚡️⚡️⚡️⚡️⚡️⚡️⚡️⚡️⚡️","✨🌟✨🌟✨🌟✨🌟✨🌟","💎💠💎💠💎💠💎💠💎💠"]:
        await msg.edit(neon)
        await asyncio.sleep(0.3)
    await msg.edit(
        f"✅ **{bot_name}** ishga tushdi!\n\n"
        f"👤 **Foydalanuvchi:** {username}\n"
        f"🔌 **Pluginlar:** {len(loaded)}\n"
        f"❌ **Xato:** {len(failed)}\n\n"
        f"⚡️ Tayyor! `.help` — buyruqlar"
    )

async def main():
    await client.start()
    print("[OK] Telegram ga ulandi!")
    try:
        await startup_animation()
    except Exception as e:
        print(f"[INFO] Animatsiya: {e}")
    await client.run_until_disconnected()

asyncio.run(main())
