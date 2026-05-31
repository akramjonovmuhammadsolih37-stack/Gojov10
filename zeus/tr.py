import asyncio
from telethon import events
import aiohttp
import json
import zeus.client
client = zeus.client.client

PLUGIN_NAME = "tr"
PLUGIN_DESC = "Tarjima (Google Translate)"
COMMANDS = {'.tr <til>': 'Xabarni tarjima qiladi. Masalan: .tr uz (reply xabar)'}

async def google_translate(text, dest="en"):
    """gpytranslate o'rniga to'g'ridan-to'g'ri Google Translate API"""
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "auto",
        "tl": dest,
        "dt": "t",
        "q": text
    }
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json(content_type=None)
    translated = "".join([item[0] for item in data[0] if item[0]])
    src_lang = data[2] if len(data) > 2 else "auto"
    return translated, src_lang

@client.on(events.NewMessage(pattern=r"\.tr ?(.*)", outgoing=True))
async def tr(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1).strip()

    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if not previous_message:
            await event.edit("**Reply xabar topilmadi!**")
            return
        text = previous_message.message
        lan = input_str or "en"
    elif "|" in input_str:
        lan, text = input_str.split("|", 1)
        lan = lan.strip()
        text = text.strip()
    elif input_str:
        # .tr uz Salom dunyo — birinchi so'z til, qolgani matn
        parts = input_str.split(" ", 1)
        if len(parts) == 2:
            lan, text = parts
        else:
            await event.edit("**Ishlatish:** `.tr uz` (reply xabar) yoki `.tr uz|Salom dunyo`")
            return
    else:
        await event.edit("**Ishlatish:** `.tr uz` (reply xabar) yoki `.tr uz|Salom dunyo`")
        return

    if not text:
        await event.edit("**Tarjima qilish uchun matn kerak!**")
        return

    try:
        translated_text, src_lang = await google_translate(text, dest=lan)
        output_str = f"🌐 **Asl til:** `{src_lang}`\n🔄 **Tarjima tili:** `{lan}`\n\n📝 **Tarjima:**\n{translated_text}"
        await event.edit(output_str)
    except aiohttp.ClientConnectorError:
        await event.edit("**Xatolik:** Internet ulanishi yo'q yoki API ishlamayapti")
    except asyncio.TimeoutError:
        await event.edit("**Xatolik:** So'rov vaqti tugadi (timeout)")
    except Exception as exc:
        await event.edit(f"**Xatolik:** `{exc}`")
