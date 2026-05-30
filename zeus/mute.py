from telethon import TelegramClient, events
import asyncio
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, User
import datetime
import zeus.client
client = zeus.client.client


PLUGIN_NAME = "mute"
PLUGIN_DESC = "Foydalanuvchini jim qilish"
COMMANDS = {'.mute <N>m/h/d': 'Foydalanuvchini jim qiladi'}

@events.register(events.NewMessage(pattern=r'\.mute', outgoing=True))
async def mute(event: events.NewMessage.Event):
    chat = await event.get_chat()
    reply_to_message = await event.get_reply_message()

    if not reply_to_message:
        await event.delete()
        return

    time_flags_dict = {
        "m": [60, "daqiqa"],
        "h": [3600, "soat"],
        "d": [86400, "kun"]
    }

    try:
        time_type = event.message.text[-1]
        count = int(event.message.text.split()[1][:-1])
        count_seconds = count * time_flags_dict[time_type][0]

        rights = ChatBannedRights(
            until_date=datetime.datetime.utcnow() + datetime.timedelta(seconds=count_seconds),
            send_messages=True
        )

        await client(EditBannedRequest(chat.id, reply_to_message.sender_id, rights))
        await event.edit(f'{count} {time_flags_dict[time_type][1]} jim qilindi')

    except KeyError:
        await event.edit("**Ishlatish:** `.mute 10m` yoki `.mute 2h` yoki `.mute 1d`")
    except Exception as e:
        await event.edit(f"**Xatolik:** `{e}`")
