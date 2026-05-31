from telethon import TelegramClient, events
import asyncio
import zeus.client
client = zeus.client.client

PLUGIN_NAME = "dump"
PLUGIN_DESC = "Dump animatsiyasi"
COMMANDS = {'.dump': 'Dump animatsiyasi'}

@client.on(events.NewMessage(pattern=r"^\.dump ?(.*)", outgoing=True))
async def dump(message):
    try:
        obj = message.pattern_match.group(1)
        if len(obj) != 3:
            raise IndexError
        inp = ' '.join(obj)
    except IndexError:
        inp = "🥞 🎂 🍫"

    u, t, g, o, s = inp.split(), '🗑', '<(^_^ <)', '(> ^_^)>', '⠀ '
    h = [(u[0], u[1], u[2]), (u[0], u[1], ''), (u[0], '', '')]

    frames = []
    for i, f in enumerate(reversed(h)):
        group = [
            ''.join(f + (s, g, s + s * f.count(''), t)),
            ''.join(f + (g, s * 2 + s * f.count(''), t)),
            ''.join(f[:i] + (o, f[i], s * 2 + s * f.count(''), t)),
            ''.join(f[:i] + (s + s * f.count(''), o, f[i], s, t)),
            ''.join(f[:i] + (s * 2 + s * f.count(''), o, f[i], t)),
            ''.join(f[:i] + (s * 3 + s * f.count(''), o, t)),
            ''.join(f[:i] + (s * 3 + s * f.count(''), g, t)),
        ]
        frames.append(group)

    for something in reversed(frames):
        for something_else in something:
            await asyncio.sleep(0.3)
            try:
                await message.edit(something_else)
            except errors.MessageIdInvalidError:
                return
