from telethon import events
from gtts import gTTS
import zeus.client
from os import remove, path

client = zeus.client.client


PLUGIN_NAME = "smsbomb"
PLUGIN_DESC = "Matnni ovozga aylantirish (TTS)"
COMMANDS = {'.tts <til>': "Matnni ovozga aylantiradi (reply xabardan)"}

@events.register(events.NewMessage(outgoing=True, pattern=r'\.tts'))
async def runj(event):
    await event.delete()
    language = event.message.raw_text.split()
    getmessage = await event.get_reply_message()
    messagelocation = event.to_id
    filename = "GOJO-SERBOT.mp3"

    if not getmessage:
        await event.client.send_message(messagelocation, "**Xabarni reply qiling!**")
        return
    if len(language) < 2:
        await event.client.send_message(messagelocation, "**Ishlatish:** `.tts uz` (til kodini kiriting)")
        return

    try:
        createtts = gTTS(text=f"{getmessage.message}", lang=f"{language[1]}", slow=False)
        createtts.save(filename)
        await client.send_file(messagelocation, filename)
        if path.exists(filename):
            remove(filename)
    except Exception as e:
        await event.client.send_message(messagelocation, f"**Xatolik:** `{e}`")
