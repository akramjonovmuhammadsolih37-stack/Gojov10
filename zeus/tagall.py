from telethon import TelegramClient, events
import zeus.client
import asyncio
client = zeus.client.client


PLUGIN_NAME = "tagall"
PLUGIN_DESC = "Hammani tag qilish"
COMMANDS = {'.tagall': "Guruh a'zolarini tag qiladi"}

@events.register(events.NewMessage(pattern=r"\.tagall", outgoing=True))
async def tagall(event):
    if event.fwd_from:
        return
    mentions = "G︎URUH AZOLARI \n"
    chat = await event.get_input_chat()
    async for x in client.iter_participants(chat, 100):
        await asyncio.sleep(0.5)
        mentions += f" \n [{x.first_name}](tg://user?id={x.id})"
        await asyncio.sleep(0.5)
        await event.edit(mentions)
