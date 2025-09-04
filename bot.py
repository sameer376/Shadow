import logging
import time
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ───────── CONFIG ─────────

BOT_TOKEN = "8267761891:AAF56sqof0Kp0ljqaN7FNOFV_hXMc-Xt2gI"
OWNER_ID = 6236477871
OWNER_USERNAME = "IG_shadow"  # without @ here
CHANNEL_LINK = "https://t.me/+it_aHo49otgwYmFl"

LOG_FILE = "logs.txt"
FILE_KEYWORDS_FILE = "file_keywords.txt"
USERS_FILE = "users.txt"
DUMP_FILE = "Dump_Skin_3.9.txt"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# ───────── HELPERS ─────────

def save_log(text: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def load_file_keywords():
    try:
        with open(FILE_KEYWORDS_FILE, "r", encoding="utf-8") as f:
            data = {}
            for line in f.read().splitlines():
                k, channel, msg_id = line.split("|")
                data[k] = (channel, int(msg_id))
            return data
    except FileNotFoundError:
        return {}

def save_file_keywords(data):
    with open(FILE_KEYWORDS_FILE, "w", encoding="utf-8") as f:
        for k, v in data.items():
            f.write(f"{k}|{v[0]}|{v[1]}\n")

def log_user(user):
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            existing = f.read().splitlines()
    except FileNotFoundError:
        existing = []
    user_string = f"{user.id}|{user.username or 'N/A'}|{user.full_name}"
    if user_string not in existing:
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(user_string + "\n")

def is_owner(user_id: int):
    return user_id == OWNER_ID

def load_dump_mapping():
    mapping_id_to_name = {}
    mapping_name_to_ids = {}
    if not os.path.exists(DUMP_FILE):
        return mapping_id_to_name, mapping_name_to_ids
    with open(DUMP_FILE, "r", encoding="utf-8") as f:
        for line in f.read().splitlines():
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3 and parts[0].isdigit():
                id_val = parts[0]
                name = parts[2] if parts[2] else "(No Name)"
                mapping_id_to_name[id_val] = name
                mapping_name_to_ids.setdefault(name.lower(), []).append(id_val)
    return mapping_id_to_name, mapping_name_to_ids

FILE_KEYWORDS = load_file_keywords()
ID2NAME, NAME2IDS = load_dump_mapping()

# ───────── MESSAGES ─────────

START_OWNER = (
    "⚡════════════════════════⚡\n\n"
    f"🚀 OWNER: @{OWNER_USERNAME}\n\n"
    "🛠 𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐟𝐮𝐥𝐥 𝐜𝐨𝐧𝐭𝐫𝐨𝐥 𝐨𝐯𝐞𝐫 𝐭𝐡𝐢𝐬 𝐛𝐨𝐭.\n\n"
    "📲 𝐓𝐲𝐩𝐞 /help 𝐭𝐨 𝐬𝐞𝐞 𝐚𝐝𝐦𝐢𝐧 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬.\n\n"
    f"🔗 𝐉𝐨𝐢𝐧 𝐨𝐮𝐫 𝐜𝐡𝐚𝐧𝐧𝐞𝐥:\n{CHANNEL_LINK}\n\n"
    "⚡════════════════════════⚡"
)

HELP_OWNER = (
    "🛠═══ 🏷 𝐎𝐖𝐍𝐄𝐑 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 🏷 ═══🛠\n\n"
    "╭──────────────────────╮\n"
    "│  📁 /set ➜ 𝐒𝐞𝐭 𝐟𝐢𝐥𝐞              │\n"
    "│  📢 /broadcast ➜ 𝐒𝐞𝐧𝐝 𝐛𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭   │\n"
    "│  📄 /logs ➜ 𝐒𝐡𝐨𝐰 𝐥𝐨𝐠𝐬             │\n"
    "│  🧹 /clearlogs ➜ 𝐂𝐥𝐞𝐚𝐫 𝐥𝐨𝐠𝐬        │\n"
    "│  📊 /stats ➜ 𝐁𝐨𝐭 𝐬𝐭𝐚𝐭𝐬            │\n"
    "│  👤 /userinfo ➜ 𝐆𝐞𝐭 𝐮𝐬𝐞𝐫 𝐢𝐧𝐟𝐨     │\n"
    "│  🏓 /ping ➜ 𝐁𝐨𝐭 𝐥𝐚𝐭𝐞𝐧𝐜𝐲            │\n"
    "│  👥 /users ➜ 𝐋𝐢𝐬𝐭 𝐚𝐥𝐥 𝐮𝐬𝐞𝐫𝐬       │\n"
    "│  📂 /allkeywords ➜ 𝐒𝐡𝐨𝐰 𝐚𝐥𝐥 𝐤𝐞𝐲𝐰𝐨𝐫𝐝𝐬 │\n"
    "│  🔢 /id2name ➜ 𝐈𝐃 𝐭𝐨 𝐍𝐚𝐦𝐞 (𝐧𝐮𝐦𝐛𝐞𝐫𝐞𝐝)    │\n"
    "│  🔤 /id2name_plain ➜ 𝐈𝐃 𝐭𝐨 𝐍𝐚𝐦𝐞 (𝐩𝐥𝐚𝐢𝐧)  │\n"
    "│  🔢 /name2id ➜ 𝐍𝐚𝐦𝐞 𝐭𝐨 𝐈𝐃 (𝐧𝐮𝐦𝐛𝐞𝐫𝐞𝐝)     │\n"
    "│  🔤 /name2id_plain ➜ 𝐍𝐚𝐦𝐞 𝐭𝐨 𝐈𝐃 (𝐩𝐥𝐚𝐢𝐧) │\n"
    "╰──────────────────────╯"
)

HELP_GENERAL = (
    "📖═══ 📌 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 📌 ═══📖\n\n"
    "💡 𝐓𝐲𝐩𝐞 𝐚 𝐤𝐞𝐲𝐰𝐨𝐫𝐝 𝐭𝐨 𝐠𝐞𝐭 𝐚 𝐟𝐢𝐥𝐞.\n"
    "✏️ 𝐄𝐱𝐚𝐦𝐩𝐥𝐞: `keyword`\n\n"
    "╭──────────────────────╮\n"
    "│  👤 /userinfo ➜ 𝐆𝐞𝐭 𝐮𝐬𝐞𝐫 𝐢𝐧𝐟𝐨      │\n"
    "│  📂 /allkeywords ➜ 𝐒𝐡𝐨𝐰 𝐚𝐥𝐥 𝐤𝐞𝐲𝐰𝐨𝐫𝐝𝐬 │\n"
    "│  🔢 /id2name ➜ 𝐈𝐃 𝐭𝐨 𝐍𝐚𝐦𝐞 (𝐧𝐮𝐦𝐛𝐞𝐫𝐞𝐝)    │\n"
    "│  🔤 /id2name_plain ➜ 𝐈𝐃 𝐭𝐨 𝐍𝐚𝐦𝐞 (𝐩𝐥𝐚𝐢𝐧)  │\n"
    "│  🔢 /name2id ➜ 𝐍𝐚𝐦𝐞 𝐭𝐨 𝐈𝐃 (𝐧𝐮𝐦𝐛𝐞𝐫𝐞𝐝)     │\n"
    "│  🔤 /name2id_plain ➜ 𝐍𝐚𝐦𝐞 𝐭𝐨 𝐈𝐃 (𝐩𝐥𝐚𝐢𝐧) │\n"
    "╰──────────────────────╯"
)

# ───────── COMMANDS ─────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = update.effective_user
    if is_owner(uid):
        msg = START_OWNER
    else:
        msg = (
            f"👋 Hello {user.first_name}!\n"
            "Type /help to see available commands.\n\n"
            f"🔗 Join our channel:\n{CHANNEL_LINK}\n\n"
        )
    await update.message.reply_text(msg)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_owner(uid):
        text = HELP_OWNER
    else:
        text = HELP_GENERAL
    buttons_help = [
        [InlineKeyboardButton("📩 Contact Owner", url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(buttons_help)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def allkeywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not FILE_KEYWORDS:
        await update.message.reply_text("📂 No keywords set.")
        return
    text = "📂 Keywords:\n" + "\n".join(FILE_KEYWORDS.keys())
    chunksize = 4000
    for i in range(0, len(text), chunksize):
        await update.message.reply_text(text[i:i+chunksize])

async def id2name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Provide IDs separated by spaces.")
        return
    response = []
    for idx, id_val in enumerate(context.args, 1):
        name = ID2NAME.get(id_val, "❌ Not found")
        response.append(f"{idx}. {id_val} → {name}")
    await update.message.reply_text("\n".join(response)[:4096])

async def id2name_plain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.partition(' ')[2].strip()
    if not text and update.message.reply_to_message:
        text = update.message.reply_to_message.text or ""
    if not text.strip():
        await update.message.reply_text("❌ Provide IDs after the command.")
        return
    results = []
    for line in text.split("\n"):
        ids = [x.strip() for x in line.split(',') if x.strip()]
        names = [ID2NAME.get(i, "❌ Not found") for i in ids]
        results.append(", ".join(names))
    await update.message.reply_text("\n".join(results)[:4096])

async def name2id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Provide name after the command.")
        return
    name = " ".join(context.args).lower()
    ids = NAME2IDS.get(name, [])
    if not ids:
        await update.message.reply_text("❌ Name not found.")
        return
    response = [f"{i+1}. {ids[i]}" for i in range(len(ids))]
    await update.message.reply_text("\n".join(response)[:4096])

async def name2id_plain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.partition(' ')[2].strip()
    if not text and update.message.reply_to_message:
        text = update.message.reply_to_message.text or ""
    if not text.strip():
        await update.message.reply_text("❌ Provide name after the command.")
        return
    names = [n.strip() for n in text.split(',') if n.strip()]
    results = []
    for name in names:
        ids = NAME2IDS.get(name.lower(), [])
        if ids:
            results.append(", ".join(ids))
        else:
            results.append("❌ Name not found")
    await update.message.reply_text("\n".join(results)[:4096])

async def set_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    if len(context.args) != 2:
        await update.message.reply_text("❌ Usage: /set <keyword> <t.me/something/message_id>")
        return
    keyword, link = context.args[0].lower(), context.args[1]
    link = link.replace("https://", "").replace("http://", "")
    parts = link.split("/")
    if len(parts) < 2:
        await update.message.reply_text("❌ Invalid link. Use t.me/channel/message_id format.")
        return
    channel = parts[-2]
    if not channel.startswith("@"):
        channel = "@" + channel
    try:
        message_id = int(parts[-1])
        FILE_KEYWORDS[keyword] = (channel, message_id)
        save_file_keywords(FILE_KEYWORDS)
        await update.message.reply_text(f"✅ Saved keyword: {keyword}")
        save_log(f"Set keyword: {keyword} -> {link}")
    except Exception:
        await update.message.reply_text("❌ Invalid message ID.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    msg = update.message.text.partition(' ')[2]
    if not msg.strip():
        await update.message.reply_text("❌ Usage: /broadcast <message>")
        return
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = f.read().strip().split('\n')
    except FileNotFoundError:
        await update.message.reply_text("❌ No users found")
        return
    sent, failed = 0, 0
    for line in users:
        if not line.strip():
            continue
        uid = int(line.split("|")[0])
        try:
            await context.bot.send_message(uid, msg)
            sent += 1
        except:
            failed += 1
    await update.message.reply_text(f"📢 Broadcast completed: {sent} sent, {failed} failed.")

async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    try:
        open(LOG_FILE, "r", encoding="utf-8").close()
        await update.message.reply_document(document=LOG_FILE)
    except FileNotFoundError:
        await update.message.reply_text("📄 Logs file not found.")

async def clearlogs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    open(LOG_FILE, "w").close()
    await update.message.reply_text("🧹 Logs cleared.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            total = len([x for x in f.read().splitlines() if x.strip()])
    except FileNotFoundError:
        total = 0
    await update.message.reply_text(f"📊 Stats:\n👥 Users: {total}\n🔑 Keywords: {len(FILE_KEYWORDS)}")

async def userinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = None
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
    elif context.args:
        try:
            user_id = int(context.args[0])
            user = await context.bot.get_chat(user_id)
        except:
            await update.message.reply_text("❌ Invalid User ID.")
            return
    else:
        user = update.effective_user
    await update.message.reply_text(f"👤 User Info\nID: {user.id}\nName: {user.full_name}\nUsername: @{user.username or 'N/A'}")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    m = await update.message.reply_text("🏓 Pinging...")
    elapsed = int((time.time() - start) * 1000)
    await m.edit_text(f"🏓 Pong! {elapsed} ms")

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    try:
        open(USERS_FILE, "r", encoding="utf-8").close()
        await update.message.reply_document(document=USERS_FILE)
    except FileNotFoundError:
        await update.message.reply_text("📃 Users file not found.")

async def keyword_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = update.effective_user
    if uid != OWNER_ID:
        log_user(user)
    keyword = update.message.text.lower().strip()
    if keyword in FILE_KEYWORDS:
        channel, msg_id = FILE_KEYWORDS[keyword]
        try:
            await context.bot.copy_message(chat_id=uid, from_chat_id=channel, message_id=msg_id)
            save_log(f"FILE: {uid} requested {keyword}")
        except:
            await update.message.reply_text("❌ Cannot send this file. Bot must be admin in channel.")
    else:
        await update.message.reply_text(f"❌ No file found for keyword '{keyword}'. Contact @{OWNER_USERNAME}.")

# ───────── MAIN ─────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("allkeywords", allkeywords))
    app.add_handler(CommandHandler("set", set_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("logs", logs))
    app.add_handler(CommandHandler("clearlogs", clearlogs))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("userinfo", userinfo))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("id2name", id2name))
    app.add_handler(CommandHandler("id2name_plain", id2name_plain))
    app.add_handler(CommandHandler("name2id", name2id))
    app.add_handler(CommandHandler("name2id_plain", name2id_plain))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), keyword_forward))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
