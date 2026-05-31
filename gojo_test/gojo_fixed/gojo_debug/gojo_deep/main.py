#!/usr/bin/env python3
import sys, os, importlib, glob, asyncio
sys.stdout.reconfigure(line_buffering=True)

try:
    from keep_alive import keep_alive
    keep_alive()
    print("[OK] Keep-alive ishga tushdi!")
except Exception as e:
    print(f"[INFO] Keep-alive: {e}")

import zeus.client
client = zeus.client.client

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
        module = importlib.import_module(module_name)
        # @client.on() handlers register automatically on import
        handlers = len(client.list_event_handlers())
        loaded.append(filename)
        print(f"[OK] {filename}")
    except Exception as e:
        import traceback
        failed.append(filename)
        print(f"[XATO] {filename}: {e}")
        traceback.print_exc()

print(f"\n[INFO] {len(loaded)} plugin yuklandi, {len(failed)} xato")
print(f"[INFO] Jami handlers: {len(client.list_event_handlers())}")
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
