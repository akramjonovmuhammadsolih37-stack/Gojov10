from telethon import events
from PIL import Image
import asyncio
from os import remove, path
import zeus.client
client = zeus.client.client


PLUGIN_NAME = "ar"
PLUGIN_DESC = "Rasmni PDF ga aylantirish"
COMMANDS = {'.itp': "Rasmni PDF ga aylantiradi (reply rasm ustida)"}

@events.register(events.NewMessage(outgoing=True, pattern=r'\.itp'))
async def runar(event):
    await event.edit("Processing...")
    await asyncio.sleep(1)
    await event.delete()
    messagelocation = event.to_id
    usercontent = "imageforpdf.png"
    filename = "zeus-userbot.pdf"
    try:
        targetimage = await event.get_reply_message()
        if not targetimage:
            await event.client.send_message(messagelocation, "**Rasm reply qiling!**")
            return
        downloadtargetimage = await event.client.download_media(targetimage, usercontent)
        opentargetimage = Image.open(usercontent)
        converttargetcontent = opentargetimage.convert("RGB")
        converttargetcontent.save(filename, "PDF", resolution=95)
        await event.client.send_file(messagelocation, filename)
        if path.exists(usercontent):
            remove(usercontent)
        if path.exists(filename):
            remove(filename)
    except Exception as e:
        await event.client.send_message(messagelocation, f"**Xatolik:** `{e}`")
