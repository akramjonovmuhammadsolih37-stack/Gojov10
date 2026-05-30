from telethon import TelegramClient, events
import asyncio
import random
import zeus.client
client = zeus.client.client

PLUGIN_NAME = "loading"
PLUGIN_DESC = "Yuklanish animatsiyasi"
COMMANDS = {'.loading': 'Loading animatsiyasi'}

@events.register(events.NewMessage(pattern=r"\.loading$", outgoing=True))
async def loading(event: events.NewMessage.Event):
    try:
        percentage = 0
        while percentage < 100:
            temp = 100 - percentage
            temp = temp if temp > 5 else 5
            percentage += temp / random.randint(5, 10)
            percentage = round(percentage, 2)

            progress = int(percentage // 5)
            await event.edit(f'`|{"█" * progress}{"-" * (20 - progress)}| {percentage}%`')
            await asyncio.sleep(.5)

        await asyncio.sleep(2)
        await event.delete()

    except Exception as e:
        print(e)
