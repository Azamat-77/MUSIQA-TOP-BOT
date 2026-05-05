from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import json, os, time

DB_FILE = "db.json"
LIMIT = 500

# DB
def load():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

db = load()

def reset(user):
    if user not in db:
        return
    now = int(time.time())
    if now - db[user]["day"] > 86400:
        db[user]["tap"] = 0
        db[user]["day"] = now

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = str(update.effective_user.id)

    if user not in db:
        db[user] = {"bal": 0, "tap": 0, "day": int(time.time())}

    reset(user)
    save(db)

    left = LIMIT - db[user]["tap"]

    text = f"""
🪙 TAPCOIN

━━━━━━━━━━━━
        🪙
   TAP THE COIN
━━━━━━━━━━━━

💰 Balance: {db[user]["bal"]}
⚡ Left: {left}/500
"""

    keyboard = [[InlineKeyboardButton("🪙 TAP COIN", callback_data="tap")]]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# TAP
async def tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = str(q.from_user.id)

    reset(user)

    if db[user]["tap"] >= LIMIT:
        await q.answer("❌ Limit tugadi", show_alert=True)
        return

    db[user]["bal"] += 1
    db[user]["tap"] += 1
    save(db)

    left = LIMIT - db[user]["tap"]

    text = f"""
🪙 TAPCOIN

━━━━━━━━━━━━
        🪙
   TAP THE COIN
━━━━━━━━━━━━

💰 Balance: {db[user]["bal"]}
⚡ Left: {left}/500
"""

    keyboard = [[InlineKeyboardButton("🪙 TAP COIN", callback_data="tap")]]

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# BOT
app = ApplicationBuilder().token("8601547802:AAGgxHHHDYjKemMvBjnhIY0csfXLsc_BZjM").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(tap, pattern="tap"))

app.run_polling()
