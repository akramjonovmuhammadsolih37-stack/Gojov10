from telethon import events
import zeus.client
from telethon.tl.functions.users import GetFullUserRequest
from os import remove, path

client = zeus.client.client


PLUGIN_NAME = "userinfo"
PLUGIN_DESC = "Foydalanuvchi ma'lumotlari"
COMMANDS = {'.userinfo': "Foydalanuvchi haqida ma'lumot"}

@events.register(events.NewMessage(outgoing=True, pattern=r'\.userinfo'))
async def userinfo(event):
    await event.delete()
    try:
        getinformation = await event.get_reply_message()
        if not getinformation:
            await event.client.send_message(event.to_id, "**Xabarni reply qiling!**")
            return
        targetid = getinformation.sender_id
        targetdetails = await client(GetFullUserRequest(targetid))
        messagelocation = event.to_id
        client.parse_mode = "html"

        user = targetdetails.users[0]
        username = f"@{user.username}" if user.username else "Yo'q"
        first_name = user.first_name or ""
        last_name = user.last_name or "Yo'q"
        phone = user.phone or "Yashirin"
        about = targetdetails.full_user.about or "Yo'q"
        dc_id = user.photo.dc_id if user.photo else "Noma'lum"

        userimage = await client.download_profile_photo(targetid)

        caption = (
            f"👤 NickName: {first_name}\n"
            f"👤 Familyasi: {last_name}\n"
            f"🔗 Username: {username}\n"
            f"🆔 User ID: {user.id}\n"
            f"☎️ Tel nomeri: {phone}\n"
            f"📎 User Link: <a href='tg://user?id={targetid}'>Profile</a>\n"
            f"📝 Bio: {about}\n"
            f"🌐 Data Center ID: {dc_id}\n"
            f"🤖 Bot: {user.bot}\n"
            f"👥 O'zaro guruhlar: {targetdetails.full_user.common_chats_count}\n"
            f"🚫 Blocklangan: {targetdetails.full_user.blocked}\n"
        )

        await client.send_file(messagelocation, userimage, caption=caption)
        if userimage and path.exists(userimage):
            remove(userimage)
    except Exception as e:
        await event.client.send_message(event.to_id, f"**Xatolik:** `{e}`")
