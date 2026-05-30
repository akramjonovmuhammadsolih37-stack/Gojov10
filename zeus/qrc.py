from telethon import events
import qrcode
from PIL import Image
import asyncio
from os import remove, path
import zeus.client
client = zeus.client.client

PLUGIN_NAME = "qrc"
PLUGIN_DESC = "QR kod yaratish/o'qish"
COMMANDS = {
    '.qrc create': 'QR kod yaratadi (reply xabar)',
    '.qrc scan': "QR kodni o'qiydi (reply rasm) — zbar kerak"
}

@events.register(events.NewMessage(outgoing=True, pattern=r'\.qrc'))
async def runqrc(event):
    await event.edit("Processing...")
    await asyncio.sleep(0.5)
    await event.delete()
    selectoption = event.message.raw_text.split()
    messagelocation = event.to_id
    filename = "gojo-ub.png"
    qrcodename = "qrcodeforscan.png"

    if len(selectoption) < 2:
        await event.client.send_message(messagelocation, "**Ishlatish:** `.qrc create` yoki `.qrc scan` (reply ustida)")
        return

    getuserdata = await event.get_reply_message()

    try:
        if selectoption[1] == "create":
            if not getuserdata or not getuserdata.message:
                await event.client.send_message(messagelocation, "**Matn reply qiling!**")
                return
            createqrcode = qrcode.make(getuserdata.message)
            createqrcode.save(filename)
            await event.client.send_file(messagelocation, filename, caption="QR kod tayyor ✅")
            if path.exists(filename):
                remove(filename)

        elif selectoption[1] == "scan":
            # zbar system kutubxonasi talab qilinadi
            # Linux: sudo apt install libzbar0
            # Windows: winget install zbar yoki DLL qo'lda
            try:
                from pyzbar.pyzbar import decode as pyzbar_decode
            except (ImportError, Exception) as e:
                await event.client.send_message(
                    messagelocation,
                    "**Scan ishlamayapti** — `zbar` tizim kutubxonasi kerak:\n"
                    "• Linux: `sudo apt install libzbar0`\n"
                    "• Windows: https://zbar.sourceforge.net/\n"
                    f"`{e}`"
                )
                return

            if not getuserdata:
                await event.client.send_message(messagelocation, "**Rasm reply qiling!**")
                return
            dl = await event.client.download_media(getuserdata, qrcodename)
            if not dl:
                await event.client.send_message(messagelocation, "**Rasm yuklab olinmadi!**")
                return
            result = pyzbar_decode(Image.open(qrcodename))
            if result:
                await event.client.send_message(messagelocation, f"📷 QR Ma'lumot: `{result[0].data.decode()}`")
            else:
                await event.client.send_message(messagelocation, "QR kod o'qilmadi — rasm sifatini tekshiring")
            if path.exists(qrcodename):
                remove(qrcodename)
        else:
            await event.client.send_message(messagelocation, "**Variant:** `.qrc create` yoki `.qrc scan`")

    except Exception as e:
        await event.client.send_message(messagelocation, f"**Xatolik:** `{e}`")
        for f in [filename, qrcodename]:
            if path.exists(f):
                remove(f)
