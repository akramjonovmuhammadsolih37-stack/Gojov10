from telethon import TelegramClient, events
import base64
import asyncio
import zeus.client
client = zeus.client.client

PLUGIN_NAME = "base64"
PLUGIN_DESC = "Base64 kodlash/dekodlash"
COMMANDS = {
    '.b64 en': 'Base64 kodlash (reply xabar)',
    '.b64 de': 'Base64 dekodlash (reply xabar)'
}

@client.on(events.NewMessage(outgoing=True, pattern=r'\.b64'))
async def runb64(event):
    await event.edit("Kutib turing...")
    await asyncio.sleep(0.5)
    options = event.message.raw_text.split()

    if len(options) < 2:
        await event.edit("**Ishlatish:** `.b64 en` yoki `.b64 de` (reply xabar ustida)")
        return

    selectsecretmessage = await event.get_reply_message()
    if not selectsecretmessage or not selectsecretmessage.message:
        await event.edit("**Matn bilan reply qiling!**")
        return

    try:
        if options[1] == "en":
            secretmessagebytes = selectsecretmessage.message.encode("utf-8")
            encoded = base64.b64encode(secretmessagebytes).decode("utf-8")
            await event.edit(f"🔒 **Shifrlangan:**\n`{encoded}`")

        elif options[1] == "de":
            secretkeybytes = selectsecretmessage.message.encode("utf-8")
            decoded = base64.b64decode(secretkeybytes).decode("utf-8")
            await event.edit(f"🔓 **Shifrdan chiqarilgan:**\n`{decoded}`")

        else:
            await event.edit("**Variant:** `.b64 en` (kodlash) yoki `.b64 de` (dekodlash)")

    except Exception as e:
        await event.edit(f"**Xatolik:** `{e}`")
