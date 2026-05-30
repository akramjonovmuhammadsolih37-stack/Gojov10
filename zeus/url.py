from telethon import events
from datetime import datetime
import asyncio
import pytz
import zeus.client
client = zeus.client.client


PLUGIN_NAME = "url"
PLUGIN_DESC = "Vaqtni ko'rsatish (.wc)"
COMMANDS = {'.wc show <timezone>': "Vaqtni ko'rsatadi (masalan: .wc show Asia/Tashkent)"}

@events.register(events.NewMessage(outgoing=True, pattern=r'\.wc'))
async def runus(event):
    await event.edit("Checking...")
    await asyncio.sleep(1)
    await event.delete()
    selectoption = event.message.raw_text.split()
    messagelocation = event.to_id
    try:
        if selectoption[1] == "show":
            localtimezone = pytz.timezone(f"{selectoption[2]}")
            localtime = datetime.now(localtimezone)
            currenttime = localtime.strftime("%I:%M %p")
            currentdate = localtime.strftime("%d %B %Y")
            await event.client.send_message(messagelocation, f"Bugun: {currentdate}\nHozirgi vaqt: {currenttime}")
        else:
            await event.client.send_message(messagelocation, "Noto'g'ri variant. Masalan: `.wc show Asia/Tashkent`")
    except IndexError:
        await event.client.send_message(messagelocation, "Variant tanlang. Masalan: `.wc show Asia/Tashkent`")
    except pytz.exceptions.UnknownTimeZoneError:
        await event.client.send_message(messagelocation, "Noma'lum vaqt zonasi. Masalan: `Asia/Tashkent`, `Europe/London`")
    except Exception as e:
        await event.client.send_message(messagelocation, f"**Xatolik:** `{e}`")
