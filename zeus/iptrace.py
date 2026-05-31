from telethon import events
import asyncio
import aiohttp
import json
import zeus.client
client = zeus.client.client

PLUGIN_NAME = "iptrace"
PLUGIN_DESC = "IP tekshirish"
COMMANDS = {'.iptrace <ip>': 'IP manzilni tekshiradi. Masalan: .iptrace 8.8.8.8'}

@client.on(events.NewMessage(outgoing=True, pattern=r'\.iptrace'))
async def iptrace(event):
    getip = event.message.raw_text.split()
    messagelocation = event.to_id

    if len(getip) < 2:
        await event.edit("**Ishlatish:** `.iptrace 8.8.8.8`")
        return

    targetip = getip[1]
    await event.edit(f"🔍 `{targetip}` tekshirilmoqda...")

    url = f"https://ip-api.com/json/{targetip}"
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await event.edit(f"**API xatosi:** HTTP {resp.status}")
                    return
                information = await resp.json(content_type=None)

        if information.get("status") == "fail":
            await event.edit(f"**Xatolik:** `{information.get('message', 'IP topilmadi')}`")
            return

        await event.edit(
            f"🌐 **IP:** `{information.get('query', targetip)}`\n"
            f"🏳️ **Mamlakat:** `{information.get('country', '?')} ({information.get('countryCode', '?')})`\n"
            f"📍 **Mintaqa:** `{information.get('regionName', '?')}`\n"
            f"🏙️ **Shahar:** `{information.get('city', '?')}`\n"
            f"📮 **Zip:** `{information.get('zip', '?')}`\n"
            f"🗺️ **Koordinat:** `{information.get('lat', '?')}, {information.get('lon', '?')}`\n"
            f"🕐 **Vaqt zonasi:** `{information.get('timezone', '?')}`\n"
            f"📡 **ISP:** `{information.get('isp', '?')}`\n"
            f"🏢 **Tashkilot:** `{information.get('org', '?')}`\n"
            f"🔢 **ASN:** `{information.get('as', '?')}`"
        )

    except aiohttp.ClientConnectorError:
        await event.edit("**Xatolik:** Internet ulanishi yo'q yoki API serverga ulab bo'lmadi")
    except asyncio.TimeoutError:
        await event.edit("**Xatolik:** So'rov vaqti tugadi (timeout). Qayta urinib ko'ring")
    except Exception as e:
        await event.edit(f"**Kutilmagan xatolik:** `{e}`")
