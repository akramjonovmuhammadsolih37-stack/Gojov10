from telethon import TelegramClient, events
import zeus.client
client = zeus.client.client

@events.register(events.NewMessage(outgoing=True, pattern=r'\.nq'))
async def nq(event):
    chat = await event.get_chat()
    replied_msg = await event.get_reply_message()
    if not replied_msg:
        await event.edit("**Reply xabar ustida ishlating!**")
        return
    await event.edit("Kutilmoqda...")
    try:
        x = await replied_msg.forward_to('@shittyquotebot')
        async with client.conversation('@shittyquotebot') as conv:
            xx = await conv.get_response(x.id)
            await client.send_read_acknowledge(conv.chat_id)
            await client.send_message(chat, xx)
            await event.message.delete()
    except Exception as e:
        await event.edit(f"**Xatolik:** `{e}`")
