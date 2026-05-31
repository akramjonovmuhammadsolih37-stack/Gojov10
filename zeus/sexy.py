from telethon import TelegramClient, events
import asyncio
import zeus.client
client = zeus.client.client

PLUGIN_NAME = "sexy"
PLUGIN_DESC = "18+ animatsiya"
COMMANDS = {'.sexy': '18+ animatsiya'}

@client.on(events.NewMessage(pattern=r"\.sexy", outgoing=True))
async def sexy(event):
    if event.fwd_from:
        return

    animation_interval = 2
    animation_ttl = range(0, 15)

    await event.edit(" sexy animation")

    animation_chars = [
        "one ❤ story️ ",
        "  😐             😕 \n/👕\\         <👗\\ \n 👖               /|",
        "  😉          😳 \n/👕\\       /👗\\ \n  👖            /|",
        "  😚            😒 \n/👕\\         <👗> \n  👖             /|",
        "  😍         ☺️ \n/👕\\      /👗\\ \n  👖          /|",
        "  😍          😍 \n/👕\\       /👗\\ \n  👖           /|",
        "  😘   😊 \n /👕\\/👗\\ \n   👖   /|",
        " 😳  😁 \n /|\\ /👙\\ \n /     / |",
        "😈    /😰\\ \n<|\\ 👙 \n /🍆    / |",
        "😅 \n/(),✊😮 \n /\\         _/\\/|",
        "😎 \n/\\_,__😫 \n  //    //       \\",
        "😖 \n/\\_,💦_😋  \n  //         //        \\",
        "  😭      ☺️ \n  /|\\ /(👶)\\ \n  /!\\ / \\ ",
        "Tugadi 😂..."
    ]

    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await event.edit(animation_chars[i % 14])
