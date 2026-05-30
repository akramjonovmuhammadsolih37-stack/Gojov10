# 🥷 GOJO-USERBOT — Yangi Plugin Qo'shish

## ✅ Eng oson yo'l (1 fayl qo'shing, shu bo'ldi!)

1. `zeus/plugin_template.py` faylini nusxalab yangi nom bering:
   ```
   cp zeus/plugin_template.py zeus/mening_pluginim.py
   ```

2. Faylni oching va quyidagilarni o'zgartiring:
   ```python
   PLUGIN_NAME = "mening_pluginim"     # ← ismni o'zgartiring
   PLUGIN_DESC = "Nimadur qiladi"      # ← tavsif
   COMMANDS = {
       ".buyruq": "Nima qiladi",       # ← buyruqlarni yozing
   }
   ```

3. Handler funksiyani yozing:
   ```python
   @events.register(events.NewMessage(outgoing=True, pattern=r"\.buyruq"))
   async def handler(event):
       await event.edit("Javob!")
   ```

4. Botni qayta ishga tushiring. **Boshqa hech narsa kerak emas!**

---

## 📋 Plugin tuzilishi (to'liq misol)

```python
from telethon import events
import zeus.client

client = zeus.client.client

PLUGIN_NAME = "ping"
PLUGIN_DESC = "Ping tekshirish"
COMMANDS = {".ping": "Bot javob vaqtini ko'rsatadi"}

@events.register(events.NewMessage(outgoing=True, pattern=r"\.ping"))
async def ping_handler(event):
    await event.edit("🏓 Pong!")
```

---

## 🗂 Fayl tuzilmasi

```
userbot/
├── main.py            ← Avtomatik barcha pluginlarni yuklaydi
├── requirements.txt
├── .env.example
├── QOSHISH.md         ← Shu fayl
└── zeus/
    ├── client.py      ← Telegram client (o'zgartirmang)
    ├── plugin_template.py  ← Yangi plugin shabloni
    ├── alive.py
    ├── spam.py
    ├── afk.py
    └── ... (boshqa pluginlar)
```

---

## ⚠️ Qoidalar

| Qoida | Izoh |
|-------|------|
| Fayl nomi | `zeus/` papkasiga `.py` fayl |
| `client.py` ni o'zgartirma | U asosiy ulanish fayli |
| `PLUGIN_NAME` belgilanmasa | `.help` da ko'rinmaydi |
| Xato bo'lsa | Bot to'xtamaydi, faqat xato chiqadi |

