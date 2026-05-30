"""
GOJO-USERBOT — .help plugin
Barcha yuklangan pluginlarning buyruqlarini chiroyli ko'rsatadi.
"""
from telethon import events
import os
import zeus.client
import importlib, glob, os

client = zeus.client.client

PLUGIN_NAME = "help"
PLUGIN_DESC = "Barcha buyruqlarni ko'rsatadi"
COMMANDS = {
    ".help":          "Barcha buyruqlar ro'yxati",
    ".help <plugin>": "Bitta plugin haqida batafsil",
}

# ── Kategoriyalar (plugin nomi → kategoriya) ─────────────────────────
CATEGORIES = {
    "🎭 Animatsiyalar": ["animation", "animation2", "bombs", "loading", "dump",
                         "sexy", "snow", "react", "fuck"],
    "🛠 Vositalar":     ["tr", "base64", "qrc", "url", "rev", "code", "emojify",
                         "ar", "type"],
    "👤 Foydalanuvchi": ["alive", "rename", "userinfo", "afk", "timer"],
    "👥 Guruh":         ["tagall", "mute", "chatinfo", "spam"],
    "🔍 Boshqa":        [],   # Kategoriyasiz pluginlar shu yerga tushadi
}

SKIP = {"client.py", "__init__.py", "plugin_template.py", "helpp.py",
        "help.py", "test.py", "testplugin.py", "magicrun.py", "magic.py",
        "emoji.py", "emojify.py"}

# ─────────────────────────────────────────────────────────────────────

def _load_plugins():
    result = {}
    plugin_files = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "*.py")))
    for filepath in plugin_files:
        fname = os.path.basename(filepath)
        if fname in SKIP:
            continue
        try:
            mod = importlib.import_module(f"zeus.{fname[:-3]}")
            name = getattr(mod, "PLUGIN_NAME", fname[:-3])
            desc = getattr(mod, "PLUGIN_DESC", "")
            cmds = getattr(mod, "COMMANDS", {})
            if cmds:
                result[name] = {"desc": desc, "cmds": cmds}
        except Exception:
            pass
    return result


def _build_help(plugins: dict) -> str:
    # Kategoriyalarga joylashtirish
    categorized = {cat: [] for cat in CATEGORIES}
    placed = set()

    for cat, names in CATEGORIES.items():
        if cat == "🔍 Boshqa":
            continue
        for pname in names:
            if pname in plugins:
                categorized[cat].append(pname)
                placed.add(pname)

    for pname in plugins:
        if pname not in placed:
            categorized["🔍 Boshqa"].append(pname)

    total_cmds = sum(len(p["cmds"]) for p in plugins.values())
    total_plugins = len(plugins)

    lines = [
        "╔═══════════════════════════════╗",
        "║   🥷  **GOJO-USERBOT**  🥷   ║",
        "╚═══════════════════════════════╝",
        "",
        f"📦 **{total_plugins}** plugin  •  ⚡ **{total_cmds}** buyruq",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]

    for cat, names in categorized.items():
        if not names:
            continue
        lines.append(f"**{cat}**")
        for pname in names:
            info = plugins[pname]
            cmd_list = "  ".join(f"`{c}`" for c in info["cmds"])
            lines.append(f"  ┣ **{pname}** — {cmd_list}")
        lines.append("")

    lines += [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "💡 `.help <plugin>` — batafsil ma'lumot",
        "📡 @" + os.environ.get("BOT_CHANNEL", ""),
    ]
    return "\n".join(lines)


def _build_plugin_help(plugins: dict, query: str) -> str:
    query = query.strip().lower()
    info = plugins.get(query)
    if not info:
        # Try partial match
        matches = [n for n in plugins if query in n]
        if len(matches) == 1:
            info = plugins[matches[0]]
            query = matches[0]
        elif len(matches) > 1:
            return f"❓ Bir nechta topildi: {', '.join(matches)}\nTo'liq nom kiriting."
        else:
            return f"❌ **{query}** — plugin topilmadi."

    lines = [
        f"╔══════════════════════╗",
        f"║  🔌 **{query.upper()}**",
        f"╚══════════════════════╝",
        "",
    ]
    if info["desc"]:
        lines.append(f"📝 _{info['desc']}_")
        lines.append("")
    lines.append("**Buyruqlar:**")
    for cmd, cdesc in info["cmds"].items():
        lines.append(f"  `{cmd}`")
        lines.append(f"  └ {cdesc}")
    return "\n".join(lines)


@events.register(events.NewMessage(outgoing=True, pattern=r"\.help ?(.*)"))
async def help_handler(event):
    await event.edit("`⏳ Yuklanmoqda...`")
    plugins = _load_plugins()
    query = event.pattern_match.group(1).strip()

    if query:
        text = _build_plugin_help(plugins, query)
    else:
        text = _build_help(plugins)

    await event.edit(text)
