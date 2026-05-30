from telethon import TelegramClient, events
import zeus.client
import asyncio
client = zeus.client.client

HNDLR = "."

PLUGIN_NAME = "spam"
PLUGIN_DESC = "Xabar spami"
COMMANDS = {'.spam <delay> <count> <xabar>': 'Xabarni takrorlaydi'}

@events.register(events.NewMessage(outgoing=True, pattern=r"\.spam ?(.*)"))
async def delayspam(e):
    try:
        args = e.text.split(" ", 3)
        dark = float(args[1])
        count = int(args[2])
        msg = str(args[3])
    except (IndexError, ValueError):
        return await e.edit(f"**ishlatish :** `{HNDLR}spam <kechikish> <son> <xabar>`")
    await e.delete()
    try:
        for i in range(count):
            await e.respond(msg)
            await asyncio.sleep(dark)
    except Exception as u:
        await e.respond(f"**Hatolik :** `{u}`")
