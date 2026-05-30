from telethon import TelegramClient, events, functions, types, Button
from datetime import datetime
import asyncio
import zeus.client
client = zeus.client.client

PLUGIN_NAME = "timer"
PLUGIN_DESC = "Taymer va soat"
COMMANDS = {
    '.timer <soniya>': 'Taymer sanaydi',
    '.numbers <son>': 'Teskari sanash',
    '.clocku <daqiqa>': "Profilga vaqt yozadi (N daqiqa)",
    '.sda': "O'chirilgan akkauntlarni sanaydi",
    '.rda': "O'chirilgan akkauntlarni guruhdan chiqaradi",
    '.rcd': "Cheklangan kontentni yuklab oladi",
    '.rgm': "O'chirilgan xabarlarni tiklaydi",
}

@events.register(events.NewMessage(outgoing=True, pattern=r"\.timer"))
async def timer(event):
    msg = event.message.raw_text.split()
    if len(msg) < 2:
        await event.edit("**Ishlatish:** `.timer 60` (soniyalarda)")
        return
    try:
        t = int(msg[1])
    except ValueError:
        await event.edit("**Xatolik:** Raqam kiriting. Masalan: `.timer 60`")
        return

    while t > 0:
        mins = t // 60
        secs = t % 60
        await event.edit(f"`⏱ {mins}:{secs:02d}`")
        await asyncio.sleep(1)
        t -= 1
    await event.edit("`⏰ Vaqt tugadi!`")
    await asyncio.sleep(3)
    await event.delete()


@events.register(events.NewMessage(outgoing=True, pattern=r"\.numbers"))
async def numbers(event):
    msg = event.message.raw_text.split()
    if len(msg) < 2:
        await event.edit("**Ishlatish:** `.numbers 10`")
        return
    try:
        t = int(msg[1])
    except ValueError:
        await event.edit("**Xatolik:** Raqam kiriting")
        return
    await event.delete()
    while t > 0:
        await asyncio.sleep(1)
        await client.send_message(event.message.to_id, str(t))
        t -= 1


@events.register(events.NewMessage(outgoing=True, pattern=r"\.clocku"))
async def clocku(event):
    from telethon.tl.functions.account import UpdateProfileRequest
    msg = event.message.raw_text.split()
    if len(msg) < 2:
        await event.edit("**Ishlatish:** `.clocku 30` (30 daqiqa)")
        return
    try:
        t = int(msg[1]) * 60
    except ValueError:
        await event.edit("**Xatolik:** Raqam kiriting")
        return
    await event.delete()
    while t > 0:
        today = datetime.today()
        time_str = today.strftime("%B | %Y | %A | %H:%M")
        await client(UpdateProfileRequest(last_name=str(time_str)))
        await asyncio.sleep(60)
        t -= 1
    await client(UpdateProfileRequest(last_name=""))


@events.register(events.NewMessage(outgoing=True, pattern=r"\.aboutclock"))
async def aboutclock(event):
    from telethon.tl.functions.account import UpdateProfileRequest
    msg = event.message.raw_text.split()
    if len(msg) < 2:
        await event.edit("**Ishlatish:** `.aboutclock 30` (30 daqiqa)")
        return
    try:
        t = int(msg[1]) * 60
    except ValueError:
        await event.edit("**Xatolik:** Raqam kiriting")
        return
    await event.delete()
    while t > 0:
        today = datetime.today()
        time_str = today.strftime("%B | %Y | %A | %H:%M")
        await client(UpdateProfileRequest(about=str(time_str)))
        await asyncio.sleep(60)
        t -= 1
    await client(UpdateProfileRequest(about=""))


@events.register(events.NewMessage(outgoing=True, pattern=r'\.sda'))
async def runsda(event):
    await event.edit("Qidirilmoqda...")
    await asyncio.sleep(1)
    await event.delete()
    messagelocation = event.to_id
    try:
        chatname = event.chat.title
        deletedid = [u.id async for u in event.client.iter_participants(messagelocation) if u.deleted]
        count = len(deletedid)
        msg = f"{'Hech qanday' if count == 0 else count} o'chirilgan hisob{'lar' if count > 1 else ''} topildi\nGuruh: {chatname}"
        await event.client.send_message(messagelocation, msg)
    except Exception as e:
        await event.client.send_message(messagelocation, f"**Xatolik:** `{e}`")


@events.register(events.NewMessage(outgoing=True, pattern=r'\.rda'))
async def runrda(event):
    await event.edit("Kutilmoqda...")
    await asyncio.sleep(1)
    await event.delete()
    messagelocation = event.to_id
    try:
        chatname = event.chat.title
        deletedid = []
        async for users in event.client.iter_participants(messagelocation):
            if users.deleted:
                deletedid.append(users.id)
                await event.client.kick_participant(messagelocation, users.id)
        count = len(deletedid)
        msg = f"{'Hech qanday' if count == 0 else count} o'chirilgan hisob chiqarib tashlandi\nGuruh: {chatname}"
        await event.client.send_message(messagelocation, msg)
    except Exception as e:
        await event.client.send_message(messagelocation, f"**Xatolik:** `{e}`")


@events.register(events.NewMessage(outgoing=True, pattern=r'\.rcd'))
async def rundrc(event):
    await event.delete()
    try:
        getrestrictedcontent = await event.get_reply_message()
        if not getrestrictedcontent:
            return
        downloadrestrictedcontent = await getrestrictedcontent.download_media()
        if downloadrestrictedcontent:
            await event.client.send_file("me", downloadrestrictedcontent)
            from os import remove, path
            if path.exists(downloadrestrictedcontent):
                remove(downloadrestrictedcontent)
    except Exception as e:
        await event.client.send_message(event.to_id, f"**Xatolik:** `{e}`")


@events.register(events.NewMessage(outgoing=True, pattern=r'\.rts'))
async def runrts(event):
    await event.delete()
    try:
        foundrestrictedcontent = await event.get_reply_message()
        if not foundrestrictedcontent:
            return
        restricteddata = foundrestrictedcontent.message
        await event.client.send_message("me", restricteddata)
    except Exception as e:
        await event.client.send_message(event.to_id, f"**Xatolik:** `{e}`")


@events.register(events.NewMessage(outgoing=True, pattern=r'\.rgm'))
async def runrgm(event):
    await event.edit("Qayta tiklanish...")
    await asyncio.sleep(1)
    await event.delete()
    try:
        targetgroup = event.to_id
        grouplog = await event.client.get_admin_log(targetgroup, edit=False, delete=True)
        for restore in grouplog:
            await event.client.send_message("me", restore.original.action.message, silent=True)
    except Exception as e:
        await event.client.send_message(event.to_id, f"**Xatolik:** `{e}`")
