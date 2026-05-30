from telethon import TelegramClient, events

@events.register(events.NewMessage(pattern=r"\.hello", outgoing=True))
async def test(event):
	await event.edit("test")
	