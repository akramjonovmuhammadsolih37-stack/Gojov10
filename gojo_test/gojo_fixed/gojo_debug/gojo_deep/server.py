#!/usr/bin/env python3
"""
GOJO-USERBOT — Multi-User Server
SQLite baza + WebSocket real-time log va status

O'rnatish:
  pip install flask flask-cors flask-sock

Ishlatish:
  python server.py
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sock import Sock
import hashlib, secrets, time, json, os, subprocess, sys, threading
import sqlite3
from contextlib import contextmanager

# ── TELEGRAM NOTIFICATION ────────────────────────────
import urllib.request

def notify_admin(msg: str):
    """Admin Telegram ga xabar yuborish"""
    token = os.environ.get("BOT_TOKEN", "")
    chat_id = os.environ.get("ADMIN_CHAT_ID", "")
    if not token or not chat_id:
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = json.dumps({"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass



# .env faylidan SESSION_STRING o'qish
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ── SESSION SHIFRLASH ─────────────────────────────────
import base64 as _b64, hashlib as _hl

def _get_enc_key():
    """DB ichidagi session_str ni shifrlash uchun kalit — ADMIN_PASSWORD dan olinadi"""
    pw = os.environ.get("ADMIN_PASSWORD", "")
    if not pw:
        # ADMIN_PASSWORD yo'q bo'lsa — DB faylidan mashinaga xos kalit yasaymiz
        # Bu kalit har deploy da bir xil bo'lishi uchun DB_PATH dan olinadi
        pw = _hl.md5(os.path.abspath(DB_PATH).encode()).hexdigest()
    return _hl.sha256(pw.encode()).digest()

def encrypt_session(plain: str) -> str:
    """XOR + base64 — oddiy shifrlash (production uchun Fernet ishlatish tavsiya etiladi)"""
    if not plain:
        return plain
    key = _get_enc_key()
    enc = bytes([ord(c) ^ key[i % len(key)] for i, c in enumerate(plain)])
    return "enc:" + _b64.b64encode(enc).decode()

def decrypt_session(stored: str) -> str:
    """Shifrni ochish"""
    if not stored or not stored.startswith("enc:"):
        return stored  # eski formatdagi session (shifrlanmagan)
    key = _get_enc_key()
    enc = _b64.b64decode(stored[4:])
    return "".join(chr(b ^ key[i % len(key)]) for i, b in enumerate(enc))

# ─────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)
sock = Sock(app)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gojo_userbot.db")

# Har bir user uchun WebSocket ulanishlar: {username: [ws1, ws2, ...]}
ws_clients = {}
ws_lock = threading.Lock()
# Bot process lar: {username: subprocess.Popen}
bot_procs = {}

# Setup sessiyalarini tozalash uchun timeout (sekund)
SETUP_TIMEOUT = 300  # 5 daqiqa

# ══════════════════════════════════════════════════════
#  DATABASE — SQLite
# ══════════════════════════════════════════════════════

@contextmanager
def get_db():
    """Thread-safe SQLite connection context manager"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # concurrent reads
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Jadvallarni yaratish va default admin qo'shish"""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    UNIQUE NOT NULL,
                password    TEXT    NOT NULL,
                salt        TEXT    NOT NULL DEFAULT '',
                role        TEXT    NOT NULL DEFAULT 'user',
                created_at  REAL    NOT NULL DEFAULT (unixepoch('now')),
                bot_running INTEGER NOT NULL DEFAULT 0,
                bot_start   REAL    DEFAULT NULL,
                session_str TEXT    DEFAULT NULL,
                api_id      INTEGER DEFAULT NULL,
                api_hash    TEXT    DEFAULT NULL
            );

            CREATE TABLE IF NOT EXISTS tokens (
                token       TEXT PRIMARY KEY,
                username    TEXT NOT NULL,
                created_at  REAL NOT NULL DEFAULT (unixepoch('now')),
                expires_at  REAL NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS bot_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL,
                level       TEXT    NOT NULL DEFAULT 'info',
                message     TEXT    NOT NULL,
                created_at  REAL    NOT NULL DEFAULT (unixepoch('now')),
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_tokens_username  ON tokens(username);
            CREATE INDEX IF NOT EXISTS idx_logs_username    ON bot_logs(username);
            CREATE INDEX IF NOT EXISTS idx_logs_created     ON bot_logs(created_at);
        """)

        # Salt ustunini qo'shish (eski bazalar uchun migration)
        try:
            conn.execute("ALTER TABLE users ADD COLUMN salt TEXT NOT NULL DEFAULT ''")
        except Exception:
            pass

        # Token expires_at ustunini qo'shish (eski bazalar uchun migration)
        try:
            conn.execute("ALTER TABLE tokens ADD COLUMN expires_at REAL NOT NULL DEFAULT 0")
        except Exception:
            pass

        # Server qayta ishga tushganda barcha bot_running holatlarini tozalash
        conn.execute("UPDATE users SET bot_running=0, bot_start=NULL WHERE bot_running=1")

        # Default admin — faqat mavjud bo'lmasa
        exists = conn.execute(
            "SELECT 1 FROM users WHERE username = 'admin'"
        ).fetchone()
        if not exists:
            # Admin parolini muhit o'zgaruvchisidan olish, yoki tasodifiy yaratish
            admin_pw = os.environ.get("ADMIN_PASSWORD", "")
            if not admin_pw:
                admin_pw = secrets.token_urlsafe(12)
                print(f"\n{'='*50}")
                print(f"  [!] AUTO-GENERATED ADMIN PASSWORD: {admin_pw}")
                print(f"  [!] Iltimos bu parolni o'zgartiring!")
                print(f"{'='*50}\n")
            salt, pw_hash = hash_pw(admin_pw)
            conn.execute(
                "INSERT INTO users (username, password, salt, role) VALUES (?, ?, ?, ?)",
                ("admin", pw_hash, salt, "admin")
            )


# ── Oddiy in-memory rate limiter (login brute-force himoya) ──────────────
_login_attempts = {}   # {ip: [timestamp, ...]}
_rl_lock = threading.Lock()
LOGIN_MAX_ATTEMPTS = 10   # 10 daqiqada maksimum urinish
LOGIN_WINDOW = 600        # 10 daqiqa

def check_rate_limit(ip: str) -> bool:
    """True = ruxsat, False = bloklangan"""
    now = time.time()
    with _rl_lock:
        attempts = _login_attempts.get(ip, [])
        # Eski urinishlarni tozalash
        attempts = [t for t in attempts if now - t < LOGIN_WINDOW]
        _login_attempts[ip] = attempts
        if len(attempts) >= LOGIN_MAX_ATTEMPTS:
            return False
        attempts.append(now)
        _login_attempts[ip] = attempts
    return True


def hash_pw(pw: str, salt: str = None):
    """Salt bilan xavfsiz parol hashlash. (salt, hash) qaytaradi."""
    if salt is None:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        'sha256',
        pw.encode('utf-8'),
        salt.encode('utf-8'),
        iterations=260000
    ).hex()
    return salt, pw_hash


def verify_pw(pw: str, salt: str, stored_hash: str) -> bool:
    """Parolni tekshirish."""
    if not salt:
        # Eski SHA-256 formatini qo'llab-quvvatlash (migration)
        return hashlib.sha256(pw.encode()).hexdigest() == stored_hash
    _, computed = hash_pw(pw, salt)
    return computed == stored_hash


def get_user_by_token(token: str):
    """Token bo'yicha user qaytaradi yoki (None, None). Muddati o'tgan tokenlarni rad etadi."""
    now = time.time()
    with get_db() as conn:
        # Muddati o'tgan tokenlarni tozalash
        conn.execute("DELETE FROM tokens WHERE expires_at > 0 AND expires_at < ?", (now,))
        row = conn.execute(
            """SELECT u.id, u.username, u.role, u.created_at, u.bot_running, u.bot_start,
                      u.session_str, u.api_id, u.api_hash
               FROM users u
               JOIN tokens t ON t.username = u.username
               WHERE t.token = ? AND (t.expires_at = 0 OR t.expires_at > ?)""",
            (token, now)
        ).fetchone()
    if not row:
        return None, None
    return row["username"], dict(row)


def get_uptime(start_ts):
    if not start_ts:
        return "00:00:00"
    s = int(time.time() - start_ts)
    return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"


def save_log(username: str, level: str, message: str):
    """Bot logini bazaga yozish (oxirgi 500 ta saqlanadi)"""
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO bot_logs (username, level, message) VALUES (?, ?, ?)",
                (username, level, message)
            )
            # Eski loglarni tozalash — har bir user uchun 500 ta
            conn.execute("""
                DELETE FROM bot_logs
                WHERE username = ? AND id NOT IN (
                    SELECT id FROM bot_logs
                    WHERE username = ?
                    ORDER BY id DESC LIMIT 500
                )
            """, (username, username))
    except Exception:
        pass


# ── Auth decorators ──────────────────────────────────
def require_auth(f):
    from functools import wraps
    @wraps(f)
    def d(*a, **kw):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        uname, user = get_user_by_token(token)
        if not user:
            return jsonify({"success": False, "message": "Token xato yoki muddati o'tgan"}), 401
        return f(*a, username=uname, user=user, **kw)
    return d


def require_admin(f):
    from functools import wraps
    @wraps(f)
    def d(*a, **kw):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        uname, user = get_user_by_token(token)
        if not user:
            return jsonify({"success": False, "message": "Token xato yoki muddati o'tgan"}), 401
        if user.get("role") != "admin":
            return jsonify({"success": False, "message": "Admin huquqi kerak"}), 403
        return f(*a, username=uname, user=user, **kw)
    return d


# ── WebSocket yuborish ────────────────────────────────
def send_to_user(username, msg: dict):
    with ws_lock:
        clients = ws_clients.get(username, [])
        dead = []
        for ws in clients:
            try:
                ws.send(json.dumps(msg))
            except Exception:
                dead.append(ws)
        for d in dead:
            clients.remove(d)


def broadcast_log(username, level, message):
    save_log(username, level, message)
    send_to_user(username, {
        "type":    "log",
        "level":   level,
        "message": message,
        "time":    time.strftime("%H:%M:%S")
    })


def broadcast_status(username, running):
    with get_db() as conn:
        row = conn.execute(
            "SELECT bot_start FROM users WHERE username = ?", (username,)
        ).fetchone()
    start_ts = row["bot_start"] if row else None
    send_to_user(username, {
        "type":    "status",
        "running": running,
        "uptime":  get_uptime(start_ts)
    })


# ── Bot process log o'qish ───────────────────────────
def read_bot_output(username, proc):
    try:
        for line in iter(proc.stdout.readline, b""):
            text = line.decode("utf-8", errors="replace").strip()
            if not text:
                continue
            level = (
                "ok"    if "[OK]"    in text else
                "error" if "[ERROR]" in text else
                "warn"  if "[WARN]"  in text else "info"
            )
            broadcast_log(username, level, text)
    except Exception:
        pass
    finally:
        with get_db() as conn:
            conn.execute(
                "UPDATE users SET bot_running=0, bot_start=NULL WHERE username=?",
                (username,)
            )
        bot_procs.pop(username, None)
        broadcast_log(username, "warn", "Bot jarayoni to'xtadi")
        notify_admin(f"⚠️ <b>GOJO Bot to'xtadi!</b>\n👤 Foydalanuvchi: <code>{username}</code>\n🕐 Vaqt: {time.strftime('%H:%M:%S')}")
        broadcast_status(username, False)


# ── WEBSOCKET ────────────────────────────────────────
@sock.route("/ws")
def websocket(ws):
    username = None
    try:
        auth_msg = ws.receive()
        if not auth_msg:
            ws.send(json.dumps({"type": "error", "message": "Timeout"}))
            return

        data  = json.loads(auth_msg)
        token = data.get("token", "")
        uname, user = get_user_by_token(token)

        if not user:
            ws.send(json.dumps({"type": "error", "message": "Token xato yoki muddati o'tgan"}))
            return

        username = uname
        with ws_lock:
            ws_clients.setdefault(username, []).append(ws)

        with get_db() as conn:
            row = conn.execute(
                "SELECT bot_running, bot_start FROM users WHERE username=?",
                (username,)
            ).fetchone()

        ws.send(json.dumps({
            "type":     "connected",
            "username": username,
            "running":  bool(row["bot_running"]) if row else False,
            "uptime":   get_uptime(row["bot_start"] if row else None),
            "message":  f"✓ WebSocket ulandi — {username}"
        }))
        broadcast_log(username, "info", f"Panel ulandi: {username}")

        while True:
            try:
                msg = ws.receive()
                if msg is None:
                    break
                d = json.loads(msg)
                if d.get("type") == "ping":
                    ws.send(json.dumps({"type": "pong", "time": time.strftime("%H:%M:%S")}))
            except Exception:
                break

    except Exception:
        pass
    finally:
        if username:
            with ws_lock:
                lst = ws_clients.get(username, [])
                if ws in lst:
                    lst.remove(ws)


# ── Sahifa ────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    panel = os.path.join(_BASE_DIR, "userbot_panel.html")
    if os.path.exists(panel):
        return send_file(panel)
    return jsonify({"status": "ok", "message": "GOJO-USERBOT Server"})


@app.route("/setup")
def setup_page():
    setup = os.path.join(_BASE_DIR, "gojo_setup.html")
    if os.path.exists(setup):
        return send_file(setup)
    return jsonify({"status": "error", "message": "setup page not found"}), 404


# ── REGISTER ─────────────────────────────────────────
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    u = data.get("username", "").strip()
    p = data.get("password", "")
    if not u or not p:
        return jsonify({"success": False, "message": "Username va parol kerak"}), 400
    if len(u) < 3:
        return jsonify({"success": False, "message": "Username kamida 3 harf"}), 400
    if len(p) < 6:
        return jsonify({"success": False, "message": "Parol kamida 6 belgi"}), 400
    # Username faqat harf, raqam va _ bo'lishi kerak
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', u):
        return jsonify({"success": False, "message": "Username faqat harf, raqam va _ bo'lishi mumkin"}), 400
    try:
        salt, pw_hash = hash_pw(p)
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (username, password, salt, role) VALUES (?, ?, ?, 'user')",
                (u, pw_hash, salt)
            )
        return jsonify({"success": True, "message": "Ro'yxatdan o'tildi!"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Bu username band"}), 400


# ── LOGIN ─────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    ip = request.remote_addr or "unknown"
    if not check_rate_limit(ip):
        return jsonify({"success": False, "message": "Juda ko'p urinish. 10 daqiqa kuting."}), 429
    data = request.get_json() or {}
    u = data.get("username", "").strip()
    p = data.get("password", "")
    with get_db() as conn:
        row = conn.execute(
            "SELECT username, password, salt, role FROM users WHERE username=?", (u,)
        ).fetchone()
    if not row or not verify_pw(p, row["salt"], row["password"]):
        # Vaqt hujumlaridan himoya — har doim bir xil vaqt sarflanadi
        time.sleep(0.2)
        return jsonify({"success": False, "message": "Username yoki parol xato"}), 401
    token = secrets.token_hex(32)
    # Token 7 kun amal qiladi
    expires_at = time.time() + 7 * 24 * 3600
    with get_db() as conn:
        conn.execute(
            "INSERT INTO tokens (token, username, expires_at) VALUES (?, ?, ?)",
            (token, u, expires_at)
        )
    return jsonify({"success": True, "token": token, "username": u, "role": row["role"]})


# ── LOGOUT ────────────────────────────────────────────
@app.route("/api/logout", methods=["POST"])
@require_auth
def logout(username, user):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    with get_db() as conn:
        conn.execute("DELETE FROM tokens WHERE token=?", (token,))
    return jsonify({"success": True})


# ── PAROL O'ZGARTIRISH ────────────────────────────────
@app.route("/api/user/change_password", methods=["POST"])
@require_auth
def change_password(username, user):
    data = request.get_json() or {}
    old_pw = data.get("old_password", "")
    new_pw = data.get("new_password", "")
    if not old_pw or not new_pw:
        return jsonify({"success": False, "message": "Eski va yangi parol kerak"}), 400
    if len(new_pw) < 6:
        return jsonify({"success": False, "message": "Yangi parol kamida 6 belgi"}), 400
    # Eski parolni tekshirish
    with get_db() as conn:
        row = conn.execute(
            "SELECT password, salt FROM users WHERE username=?", (username,)
        ).fetchone()
    if not row or not verify_pw(old_pw, row["salt"], row["password"]):
        time.sleep(0.2)
        return jsonify({"success": False, "message": "Eski parol xato"}), 401
    salt, pw_hash = hash_pw(new_pw)
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET password=?, salt=? WHERE username=?",
            (pw_hash, salt, username)
        )
        # Barcha tokenlarni o'chirish — qayta login talab qilinadi
        conn.execute("DELETE FROM tokens WHERE username=?", (username,))
    return jsonify({"success": True, "message": "Parol muvaffaqiyatli o'zgartirildi. Qayta kiring."})


# ── BOT STATUS ────────────────────────────────────────
@app.route("/api/bot/status", methods=["GET"])
@require_auth
def bot_status(username, user):
    return jsonify({
        "success": True,
        "running": bool(user.get("bot_running")),
        "uptime":  get_uptime(user.get("bot_start"))
    })


# ── BOT LOGS (tarix) ──────────────────────────────────
@app.route("/api/bot/logs", methods=["GET"])
@require_auth
def bot_logs(username, user):
    try:
        limit = min(int(request.args.get("limit", 100)), 500)
    except (ValueError, TypeError):
        limit = 100
    with get_db() as conn:
        rows = conn.execute(
            """SELECT level, message, created_at FROM bot_logs
               WHERE username=? ORDER BY id DESC LIMIT ?""",
            (username, limit)
        ).fetchall()
    logs = [{"level": r["level"], "message": r["message"],
             "time": time.strftime("%H:%M:%S", time.localtime(r["created_at"]))}
            for r in reversed(rows)]
    return jsonify({"success": True, "logs": logs})


# ── BOT START ─────────────────────────────────────────
@app.route("/api/bot/start", methods=["POST"])
@require_auth
def bot_start(username, user):
    if user.get("bot_running"):
        return jsonify({"success": False, "message": "Bot allaqachon ishlamoqda"})

    bot_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    if os.path.exists(bot_script):
        try:
            bot_env = os.environ.copy()
            # Foydalanuvchining session va API ma'lumotlarini subprocess ga uzatish
            with get_db() as _conn:
                _row = _conn.execute(
                    "SELECT session_str, api_id, api_hash FROM users WHERE username=?",
                    (username,)
                ).fetchone()
            if _row:
                if _row["session_str"]:
                    bot_env["SESSION_STRING"] = decrypt_session(_row["session_str"])
                if _row["api_id"]:
                    bot_env["API_ID"] = str(_row["api_id"])
                if _row["api_hash"]:
                    bot_env["API_HASH"] = _row["api_hash"]
            proc = subprocess.Popen(
                [sys.executable, bot_script],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                bufsize=1,
                env=bot_env,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            bot_procs[username] = proc
            t = threading.Thread(target=read_bot_output, args=(username, proc), daemon=True)
            t.start()
            broadcast_log(username, "ok", f"Bot jarayoni ishga tushirildi (PID: {proc.pid})")
        except Exception as e:
            broadcast_log(username, "error", f"Bot ishga tushmadi: {e}")
            return jsonify({"success": False, "message": f"Bot ishga tushmadi: {e}"}), 500

    now = time.time()
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET bot_running=1, bot_start=? WHERE username=?",
            (now, username)
        )
    broadcast_status(username, True)
    broadcast_log(username, "ok", "GOJO-USERBOT ishga tushirildi ✓")
    notify_admin(f"✅ <b>GOJO Bot ishga tushdi!</b>\n👤 Foydalanuvchi: <code>{username}</code>")
    return jsonify({"success": True, "message": "Bot ishga tushdi ✓"})


# ── BOT STOP ──────────────────────────────────────────
@app.route("/api/bot/stop", methods=["POST"])
@require_auth
def bot_stop(username, user):
    if not user.get("bot_running"):
        return jsonify({"success": False, "message": "Bot allaqachon to'xtagan"})

    proc = bot_procs.pop(username, None)
    if proc:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    with get_db() as conn:
        conn.execute(
            "UPDATE users SET bot_running=0, bot_start=NULL WHERE username=?",
            (username,)
        )
    broadcast_status(username, False)
    broadcast_log(username, "warn", "GOJO-USERBOT to'xtatildi")
    notify_admin(f"⛔ <b>GOJO Bot to'xtatildi</b>\n👤 Foydalanuvchi: <code>{username}</code>")
    return jsonify({"success": True, "message": "Bot to'xtatildi"})


# ── ADMIN: Barcha userlar ─────────────────────────────
@app.route("/api/admin/users", methods=["GET"])
@require_admin
def admin_users(username, user):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT username, role, created_at, bot_running, bot_start, session_str, api_id, api_hash FROM users"
        ).fetchall()
    return jsonify({"success": True, "users": [
        {"username":    r["username"],
         "role":        r["role"],
         "created":     r["created_at"],
         "bot_running": bool(r["bot_running"]),
         "uptime":      get_uptime(r["bot_start"]),
         "has_session": bool(r["session_str"]),
         "api_id":      r["api_id"],
         "api_hash":    r["api_hash"]}
        for r in rows
    ]})


# ── ADMIN: User o'chirish ─────────────────────────────
@app.route("/api/admin/users/<target>", methods=["DELETE"])
@require_admin
def admin_delete(target, username, user):
    if target == "admin":
        return jsonify({"success": False, "message": "Adminni o'chirib bo'lmaydi"}), 400
    with get_db() as conn:
        exists = conn.execute(
            "SELECT 1 FROM users WHERE username=?", (target,)
        ).fetchone()
        if not exists:
            return jsonify({"success": False, "message": "User topilmadi"}), 404
        # Bot ishlab turgan bo'lsa to'xtatish
        proc = bot_procs.pop(target, None)
        if proc:
            try: proc.terminate()
            except Exception: pass
        conn.execute("DELETE FROM users WHERE username=?", (target,))
    return jsonify({"success": True, "message": f"{target} o'chirildi"})


# ── ADMIN: Role o'zgartirish ──────────────────────────
@app.route("/api/admin/users/<target>/role", methods=["POST"])
@require_admin
def admin_role(target, username, user):
    # Admin o'zini yoki bosh adminni o'zgartira olmaydi
    if target == "admin":
        return jsonify({"success": False, "message": "Bosh adminning rolini o'zgartirib bo'lmaydi"}), 400
    data = request.get_json() or {}
    role = data.get("role", "user")
    if role not in ("admin", "user"):
        return jsonify({"success": False, "message": "Noto'g'ri rol"}), 400
    with get_db() as conn:
        exists = conn.execute(
            "SELECT 1 FROM users WHERE username=?", (target,)
        ).fetchone()
        if not exists:
            return jsonify({"success": False, "message": "User topilmadi"}), 404
        conn.execute("UPDATE users SET role=? WHERE username=?", (role, target))
    return jsonify({"success": True, "message": f"{target} → {role}"})


# ── ADMIN: Bot boshqarish ─────────────────────────────
@app.route("/api/admin/users/<target>/bot/<action>", methods=["POST"])
@require_admin
def admin_bot(target, action, username, user):
    with get_db() as conn:
        exists = conn.execute(
            "SELECT 1 FROM users WHERE username=?", (target,)
        ).fetchone()
        if not exists:
            return jsonify({"success": False, "message": "Topilmadi"}), 404
        if action == "start":
            conn.execute(
                "UPDATE users SET bot_running=1, bot_start=? WHERE username=?",
                (time.time(), target)
            )
            broadcast_log(target, "ok", "Admin tomonidan bot ishga tushirildi")
            broadcast_status(target, True)
        elif action == "stop":
            proc = bot_procs.pop(target, None)
            if proc:
                try: proc.terminate()
                except Exception: pass
            conn.execute(
                "UPDATE users SET bot_running=0, bot_start=NULL WHERE username=?",
                (target,)
            )
            broadcast_log(target, "warn", "Admin tomonidan bot to'xtatildi")
            broadcast_status(target, False)
        else:
            return jsonify({"success": False, "message": "Noto'g'ri amal"}), 400
    return jsonify({"success": True, "message": f"{target} bot {action}"})


# ── SESSION SETUP ─────────────────────────────────────
_setup_clients = {}
_setup_lock    = threading.Lock()


def _cleanup_setup_sessions():
    """Muddati o'tgan setup sessiyalarini tozalash"""
    now = time.time()
    with _setup_lock:
        expired = [k for k, v in _setup_clients.items()
                   if now - v.get("created_at", now) > SETUP_TIMEOUT]
        for k in expired:
            entry = _setup_clients.pop(k)
            loop = entry.get("loop")
            client = entry.get("client")
            # Asinxron klientni yopish
            if client and loop:
                try:
                    import asyncio
                    asyncio.run_coroutine_threadsafe(client.disconnect(), loop)
                except Exception:
                    pass


# Har 60 soniyada eski sessiyalarni tozalash
def _start_cleanup_thread():
    def _run():
        while True:
            time.sleep(60)
            try:
                _cleanup_setup_sessions()
            except Exception:
                pass
    t = threading.Thread(target=_run, daemon=True)
    t.start()


@app.route("/api/setup/send_code", methods=["POST"])
@require_auth
def setup_send_code(username, user):
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
    except ImportError:
        return jsonify({"success": False, "message": "telethon o'rnatilmagan"}), 500

    data     = request.get_json() or {}
    phone    = data.get("phone", "").strip()
    try:
        api_id = int(data.get("api_id", 0))
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "API_ID butun son bo'lishi kerak"}), 400
    api_hash = data.get("api_hash", "").strip()

    if not phone or not api_id or not api_hash:
        return jsonify({"success": False, "message": "Telefon, API_ID va API_HASH kerak"}), 400

    # Foydalanuvchining oldingi setup sessiyasini tozalash
    with _setup_lock:
        old_keys = [k for k, v in _setup_clients.items() if v.get("owner") == username]
        for k in old_keys:
            old_entry = _setup_clients.pop(k)
            try:
                old_loop = old_entry.get("loop")
                old_client = old_entry.get("client")
                if old_client and old_loop:
                    import asyncio
                    asyncio.run_coroutine_threadsafe(old_client.disconnect(), old_loop)
            except Exception:
                pass

    setup_id = secrets.token_hex(16)

    async def _send():
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        result = await client.send_code_request(phone)
        return client, result.phone_code_hash

    import asyncio
    loop = asyncio.new_event_loop()
    try:
        client, phone_code_hash = loop.run_until_complete(_send())
        with _setup_lock:
            _setup_clients[setup_id] = {
                "client": client, "phone": phone,
                "phone_code_hash": phone_code_hash,
                "api_id": api_id, "api_hash": api_hash,
                "loop": loop,
                "owner": username,
                "created_at": time.time()
            }
        return jsonify({"success": True, "setup_id": setup_id, "message": "Kod yuborildi ✓"})
    except Exception as e:
        try:
            loop.close()
        except Exception:
            pass
        return jsonify({"success": False, "message": f"Xato: {str(e)}"}), 400


@app.route("/api/setup/verify_code", methods=["POST"])
@require_auth
def setup_verify_code(username, user):
    data     = request.get_json() or {}
    setup_id = data.get("setup_id", "")
    code     = data.get("code", "").strip()
    password = data.get("password", "").strip()

    with _setup_lock:
        entry = _setup_clients.get(setup_id)
    if not entry:
        return jsonify({"success": False, "message": "Setup sessiyasi topilmadi yoki muddati o'tgan"}), 400

    # Setup sessiyasi bu userga tegishli ekanligini tekshirish
    if entry.get("owner") != username:
        return jsonify({"success": False, "message": "Ruxsat yo'q"}), 403

    client = entry["client"]
    loop   = entry["loop"]

    async def _verify():
        try:
            await client.sign_in(entry["phone"], code,
                                 phone_code_hash=entry["phone_code_hash"])
        except Exception as e:
            err = str(e).lower()
            if "two-steps" in err or "password" in err or "2fa" in err:
                if not password:
                    raise ValueError("2FA_REQUIRED")
                await client.sign_in(password=password)
        session_str = client.session.save()
        await client.disconnect()
        return session_str

    try:
        session_str = loop.run_until_complete(_verify())
        loop.close()
        with _setup_lock:
            _setup_clients.pop(setup_id, None)

        # Bazaga saqlash
        with get_db() as conn:
            conn.execute(
                "UPDATE users SET session_str=?, api_id=?, api_hash=? WHERE username=?",
                (encrypt_session(session_str), entry["api_id"], entry["api_hash"], username)
            )

        # .env ham yangilash (main.py uchun)
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        lines    = []
        updated  = False
        if os.path.exists(env_path):
            with open(env_path) as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith("SESSION_STRING="):
                    lines[i] = f"SESSION_STRING={session_str}\n"
                    updated = True
                    break
        if not updated:
            lines.append(f"SESSION_STRING={session_str}\n")
        with open(env_path, "w") as f:
            f.writelines(lines)

        os.environ["SESSION_STRING"] = session_str

        return jsonify({
            "success": True,
            "session_string": session_str,  # foydalanuvchiga bir marta ko'rsatiladi, bazada shifrlangan
            "message": "Session muvaffaqiyatli saqlandi! ✓"
        })
    except ValueError as e:
        if "2FA_REQUIRED" in str(e):
            return jsonify({"success": False, "message": "2FA_REQUIRED", "need_2fa": True})
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Xato: {str(e)}"}), 400


@app.route("/api/setup/status", methods=["GET"])
@require_auth
def setup_status(username, user):
    session_raw = user.get("session_str") or ""
    # .env fallback
    _env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not session_raw and os.path.exists(_env_file):
        with open(_env_file) as f:
            for line in f:
                if line.startswith("SESSION_STRING="):
                    session_raw = line.split("=", 1)[1].strip()
                    break
    has_session = bool(session_raw)
    return jsonify({
        "success":     True,
        "has_session": has_session,
        "preview":     f"***...{len(decrypt_session(session_raw))} belgi" if has_session else ""
    })



# ── ADMIN: User session ko\'rish ───────────────────────
@app.route("/api/admin/users/<target>/session", methods=["GET"])
@require_admin
def admin_get_session(target, username, user):
    with get_db() as conn:
        row = conn.execute(
            "SELECT session_str, api_id, api_hash FROM users WHERE username=?", (target,)
        ).fetchone()
    if not row:
        return jsonify({"success": False, "message": "User topilmadi"}), 404
    stored = row["session_str"] or ""
    plain  = decrypt_session(stored) if stored else ""
    return jsonify({
        "success":        True,
        "has_session":    bool(plain),
        "session_string": plain,
        "api_id":         row["api_id"],
        "api_hash":       row["api_hash"],
        "length":         len(plain)
    })


# ── ADMIN: User session o\'chirish ──────────────────────
@app.route("/api/admin/users/<target>/session", methods=["DELETE"])
@require_admin
def admin_delete_session(target, username, user):
    if target == "admin" and username != "admin":
        return jsonify({"success": False, "message": "Ruxsat yo\'q"}), 403
    with get_db() as conn:
        exists = conn.execute("SELECT 1 FROM users WHERE username=?", (target,)).fetchone()
        if not exists:
            return jsonify({"success": False, "message": "User topilmadi"}), 404
        conn.execute(
            "UPDATE users SET session_str=NULL, api_id=NULL, api_hash=NULL WHERE username=?",
            (target,)
        )
    return jsonify({"success": True, "message": f"{target} sessiyasi o\'chirildi"})


# ── DB STATS (qo'shimcha) ─────────────────────────────
@app.route("/api/admin/db/stats", methods=["GET"])
@require_admin
def db_stats(username, user):
    with get_db() as conn:
        users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        logs_count  = conn.execute("SELECT COUNT(*) FROM bot_logs").fetchone()[0]
        tokens_count = conn.execute("SELECT COUNT(*) FROM tokens").fetchone()[0]
        db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    return jsonify({
        "success": True,
        "users":   users_count,
        "logs":    logs_count,
        "tokens":  tokens_count,
        "db_size_kb": round(db_size / 1024, 1)
    })


# ══════════════════════════════════════════════════════
# ── /api/me — token tekshirish va user ma'lumoti ────────────
@app.route("/api/me", methods=["GET"])
@require_auth
def me(username, user):
    return jsonify({
        "success":     True,
        "username":    username,
        "role":        user.get("role", "user"),
        "bot_running": bool(user.get("bot_running")),
        "has_session": bool(user.get("session_str")),
        "uptime":      get_uptime(user.get("bot_start"))
    })


if __name__ == "__main__":
    init_db()
    _start_cleanup_thread()
    PORT = int(os.environ.get("PORT", 5000))
    print("=" * 50)
    print("  GOJO-USERBOT Multi-User Server (SQLite)")
    print(f"  DB   : {DB_PATH}")
    print(f"  URL  : http://0.0.0.0:{PORT}")
    print(f"  WS   : ws://0.0.0.0:{PORT}/ws")
    print("  [!] Admin parolini .env da ADMIN_PASSWORD orqali o'rnating")
    print("=" * 50)
    notify_admin(f"🚀 <b>GOJO Server ishga tushdi!</b>\n🌐 URL: https://gojov5-final.onrender.com")
    app.run(host="0.0.0.0", port=PORT, debug=False)
