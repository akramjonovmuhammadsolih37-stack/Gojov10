from telethon import TelegramClient, events
import asyncio
import zeus.client
client = zeus.client.client


PLUGIN_NAME = "type"
PLUGIN_DESC = "Yozish animatsiyasi"
COMMANDS = {'.type <matn>': 'Matnni bosma mashinkada yozadi'}

@events.register(events.NewMessage(outgoing=True, pattern=r'\.type'))
async def type_anim(event):
    if ".type " in event.raw_text:
        orig_text = event.raw_text.split(".type ", maxsplit=1)[1]
        text = orig_text
        pb = ""
        typing_symbol = "•"
        while pb != orig_text:
            try:
                await event.edit(pb + typing_symbol)
                await asyncio.sleep(0.05)
                pb += text[0]
                text = text[1:]
                await event.edit(pb)
                await asyncio.sleep(0.05)
            except Exception as e:
                print(e)
                break
