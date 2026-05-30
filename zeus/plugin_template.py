"""
╔══════════════════════════════════════════╗
║   GOJO-USERBOT — Yangi Plugin Shablon   ║
╚══════════════════════════════════════════╝

ISHLATISH:
  1. Bu faylni nusxalab yangi nom bering, masalan: zeus/salom.py
  2. PLUGIN_NAME, PLUGIN_DESC, COMMANDS ni to'ldiring
  3. Handler funksiyalarni yozing
  4. Shu bo'ldi! main.py avtomatik topib yuklaydi.

MISOL:
  .salom  →  "Salom, dunyo!" deb javob beradi
"""

from telethon import events
import zeus.client

client = zeus.client.client

# ── Plugin ma'lumotlari (ixtiyoriy, .help da ko'rinadi) ──────────────
PLUGIN_NAME = "shablon"          # Plugin nomi
PLUGIN_DESC = "Misol plugin"     # Qisqa tavsif
COMMANDS = {
    ".salom": "Salom deydi",
    # ".boshqa": "Boshqa buyruq tavsifi",
}
# ─────────────────────────────────────────────────────────────────────


@events.register(events.NewMessage(outgoing=True, pattern=r"\.salom"))
async def salom_handler(event):
    """Misol handler — .salom buyrug'iga javob beradi"""
    await event.edit("👋 Salom, dunyo!")


# ── Agar bir nechta handler bo'lsa, hammasi shu yerda ────────────────
# @events.register(events.NewMessage(outgoing=True, pattern=r"\.boshqa"))
# async def boshqa_handler(event):
#     await event.edit("Bu boshqa buyruq!")
