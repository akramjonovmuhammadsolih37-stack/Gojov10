from telethon import TelegramClient, events

@client.on(events.NewMessage(pattern=r"\.hello", outgoing=True))
async def test(event):
	await event.edit("test")
	