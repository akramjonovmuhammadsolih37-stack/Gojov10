from telethon import TelegramClient, events, Button
import zeus.client
client = zeus.client.client

PLUGIN_NAME = "help"
PLUGIN_DESC = "Inline help menu (bot token kerak)"
COMMANDS = {}

# botClient ixtiyoriy — faqat BOT_TOKEN berilsa ishlaydi
# main.py da ishga tushiriladi, shu sababli bu yerda faqat handler ro'yxatga olinadi
def register_bot_handlers(bot):
    @bot.on(events.InlineQuery)
    async def _(query):
        if query.text == "ppphelp":
            result = query.builder.article('ppphelp', text="GOJO USERBOT HELP MENU", buttons=[
                [Button.inline("Bombs", data=b"1"), Button.inline("magic", data=b"2"), Button.inline("loading", data=b"3")],
                [Button.inline("Dump", data=b"4"), Button.inline("18+", data=b"5"), Button.inline("LUL", data=b"6")],
            ])
            await query.answer([result])

    @bot.on(events.CallbackQuery)
    async def uzgaruvchi(event):
        answers = {
            b'1': "Animatsia bombs\nplugin: .bombs",
            b'2': "Animatsia Heart emojies\nplugin: .magic",
            b'3': "Animatsia loading\nplugin: .loading",
            b'4': "Animatsia dump\nplugin: .dump",
            b'5': "18+ animation\nplugin: .sexy",
            b'6': "LUL animation\nplugin: .lul",
        }
        await event.answer(answers.get(event.data, "Noma'lum"), alert=True)
