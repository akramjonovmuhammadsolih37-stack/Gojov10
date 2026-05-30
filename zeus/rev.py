from telethon import TelegramClient, events
import zeus.client
client = zeus.client.client

PLUGIN_NAME = "rev"
PLUGIN_DESC = "Matnni teskari qilish"
COMMANDS = {'.rev': 'Reply xabarni teskari qiladi'}

@events.register(events.NewMessage(outgoing=True, pattern=r'\.rev'))
async def rev(event):
    if not event.is_reply:
        await event.edit("**Reply xabar ustida ishlating!**")
        return
    replied = await event.get_reply_message()
    if not replied or not replied.message:
        await event.edit("**Matn topilmadi!**")
        return
    replied_msg_rev = replied.message[::-1]
    await event.client.edit_message(event.message, replied_msg_rev)
