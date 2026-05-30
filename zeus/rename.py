from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest
import zeus.client

client = zeus.client.client

PLUGIN_NAME = "rename"
PLUGIN_DESC = "Ism o'zgartirish"
COMMANDS = {'.rename <ism>//[familiya]': "Profilingiz ismini o'zgartiradi. Masalan: .rename Gojo//Satoru"}

@events.register(events.NewMessage(pattern=r"\.rename (.*)", outgoing=True))
async def rename(event):
    names = event.pattern_match.group(1).strip()
    if not names:
        await event.edit("**Ishlatish:** `.rename Ism` yoki `.rename Ism//Familiya`")
        return

    first_name = names
    last_name = ""
    if "//" in names:
        parts = names.split("//", 1)
        first_name = parts[0].strip()
        last_name = parts[1].strip()

    if not first_name:
        await event.edit("**Ism bo'sh bo'lmasligi kerak!**")
        return

    try:
        await event.client(
            UpdateProfileRequest(
                first_name=first_name,
                last_name=last_name,
            )
        )
        await event.edit(f"✅ Ism o'zgartirildi: **{first_name}** {last_name}")
    except Exception as ex:
        await event.edit(f"**Xatolik:** `{ex}`")
