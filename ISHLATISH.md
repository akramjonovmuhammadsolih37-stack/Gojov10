# GOJO-USERBOT — Render Deploy Qo'llanmasi

## 1. SESSION_STRING olish

Kompyuterda bir marta ishga tushiring:
```
pip install telethon
python get_session.py
```
Telefonga kelgan kodni kiriting — SESSION_STRING chiqadi.

## 2. Render.com da deploy

1. GitHub ga kodlarni yuklang
2. render.com ga kiring
3. **New > Background Worker** tanlang (Web Service EMAS!)
4. GitHub repo ni ulang
5. **Environment Variables** ga qo'shing:
   - `API_ID` = my.telegram.org dan
   - `API_HASH` = my.telegram.org dan
   - `SESSION_STRING` = get_session.py dan

## 3. Buyruqlar

| Buyruq | Vazifa |
|--------|--------|
| `.alive` | Bot tirikmi? |
| `.spam 1 5 salom` | 5 marta xabar |
| `.tts uz matn` | Ovozga aylantirish |
| `.help` | Barcha buyruqlar |

## 4. Yangi plugin qo'shish

`zeus/` papkasiga `.py` fayl qo'ying — avtomatik yuklanadi!
