from telethon import TelegramClient, events
import zeus.client
from zeus.magic import Magic
import asyncio

magic = Magic()
client = zeus.client.client

@events.register(events.NewMessage(outgoing=True))
async def magicrun(event):
    if '.magic' in event.raw_text:
        await asyncio.sleep(0.3)
        for d in magic.magic:
            await asyncio.sleep(0.3)
            await event.edit(d)
