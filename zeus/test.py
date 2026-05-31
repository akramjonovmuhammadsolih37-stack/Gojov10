from telethon import TelegramClient, events
import zeus.client
client = zeus.client.client

@client.on(events.NewMessage(pattern=r"\.hello", outgoing=True))
async def test(event):
	await event.edit("test")
	