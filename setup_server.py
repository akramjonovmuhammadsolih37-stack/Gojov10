#!/usr/bin/env python3
"""
GOJO-USERBOT — O'rnatish serveri
Foydalanuvchi login talab qilmasdan brauzer orqali session olishi uchun.

Ishlatish:
  pip install flask telethon
  python setup_server.py
  
Brauzerda: http://localhost:7070
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import threading, asyncio, secrets, os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
CORS(app)

_sessions = {}
_lock = threading.Lock()

@app.route("/")
@app.route("/setup")
def index():
    return send_file(os.path.join(os.path.dirname(__file__), "gojo_setup.html"))

@app.route("/api/setup/send_code", methods=["POST"])
def send_code():
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from telethon.errors import (
        ApiIdInvalidError, ApiIdPublishedFloodError,
        FloodWaitError, PhoneNumberInvalidError,
        PhoneNumberBannedError, PhoneNumberFloodError
    )
    data     = request.get_json() or {}
    phone    = str(data.get("phone","")).strip()
    api_id   = data.get("api_id")
    api_hash = str(data.get("api_hash","")).strip()

    if not phone or not api_id or not api_hash:
        return jsonify({"success": False, "error": "api_id, api_hash va phone kerak"}), 400

    try:
        api_id = int(api_id)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "api_id raqam bo'lishi kerak"}), 400

    async def _send():
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        result = await client.send_code_request(phone)
        return client, result.phone_code_hash

    try:
        loop = asyncio.new_event_loop()
        client, phone_code_hash = loop.run_until_complete(_send())
        setup_id = secrets.token_hex(16)
        with _lock:
            _sessions[setup_id] = {
                "client": client, "loop": loop,
                "phone": phone, "phone_code_hash": phone_code_hash,
                "api_id": api_id, "api_hash": api_hash
            }
        return jsonify({"success": True, "setup_id": setup_id, "message": "Kod yuborildi ✓"})
    except ApiIdInvalidError:
        return jsonify({"success": False, "error": "API ID yoki HASH noto'g'ri. my.telegram.org dan qayta tekshiring"}), 400
    except PhoneNumberInvalidError:
        return jsonify({"success": False, "error": "Telefon raqam noto'g'ri formatda. + bilan boshlang"}), 400
    except PhoneNumberBannedError:
        return jsonify({"success": False, "error": "Bu telefon raqam Telegram tomonidan bloklangan"}), 400
    except FloodWaitError as e:
        return jsonify({"success": False, "error": f"Juda ko'p urinish. {e.seconds} soniya kuting"}), 429
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/setup/verify_code", methods=["POST"])
def verify_code():
    from telethon.errors import (
        SessionPasswordNeededError, PasswordHashInvalidError,
        PhoneCodeInvalidError, PhoneCodeExpiredError
    )
    data     = request.get_json() or {}
    setup_id = data.get("setup_id","")
    code     = str(data.get("code","")).strip()
    password = data.get("password","")

    with _lock:
        entry = _sessions.get(setup_id)
    if not entry:
        return jsonify({"success": False, "error": "Sessiya topilmadi. Telefon raqamni qayta kiriting"}), 400

    client = entry["client"]
    loop   = entry["loop"]

    async def _verify():
        await client.sign_in(entry["phone"], code,
                             phone_code_hash=entry["phone_code_hash"])
        return client.session.save()

    async def _2fa(pwd):
        await client.sign_in(password=pwd)
        return client.session.save()

    try:
        session_str = loop.run_until_complete(_verify())
        with _lock:
            _sessions.pop(setup_id, None)
        return jsonify({"success": True, "session_string": session_str})

    except SessionPasswordNeededError:
        if password:
            try:
                session_str = loop.run_until_complete(_2fa(password))
                with _lock:
                    _sessions.pop(setup_id, None)
                return jsonify({"success": True, "session_string": session_str})
            except PasswordHashInvalidError:
                return jsonify({"success": False, "error": "2FA parol noto'g'ri"}), 400
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        return jsonify({"success": False, "error": "2FA kerak", "needs_2fa": True}), 401

    except PhoneCodeInvalidError:
        return jsonify({"success": False, "error": "Kod noto'g'ri. Qayta kiriting"}), 400
    except PhoneCodeExpiredError:
        return jsonify({"success": False, "error": "Kod muddati o'tgan. Qayta yuboring"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("SETUP_PORT", 7070))
    print("=" * 50)
    print("  🥷 GOJO-USERBOT — O'rnatish serveri")
    print("=" * 50)
    print(f"\n  Brauzerda oching: http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
