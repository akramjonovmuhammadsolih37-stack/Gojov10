from telethon import TelegramClient, events 
from emoji import  emojize
import os
import zeus.client
from zeus import emojify
import time
import asyncio
client = zeus.client.client


@events.register(events.NewMessage(pattern=r"\.emoji(?: |$)(.*)", outgoing=True))
async def itachi(event):
    args = event.pattern_match.group(1)
    if not args:
        get = await event.get_reply_message()
        args = get.text
    if not args:
        await event.edit("**Ishlatish:** `.emoji <matn>` yoki reply xabar ustida")
        return
    result = ""
    for a in args:
        a = a.lower()
        if a in emojify.oofman:
            char = emojify.oofman[emojify.oofman.index(a)]
            result += char
        else:
            result += a
    await event.edit(result)
    