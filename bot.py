import os
import yt_dlp
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# 🔧 BOT SOZLAMALARI
ADMIN_ID = 7562363422
BOT_TOKEN = "8331117123:AAE8BPC9yOrg8U839uVxC6Bf5BxXaL9o300"

bot = Client(
    "music_bot",
    bot_token=BOT_TOKEN,
    api_id=38920950,
    api_hash="1b2b3131134f901228acd5fa464c5eb5",
    sleep_threshold=60
)

# 📁 PAPKALAR
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

USER_FILE = "users.txt"
REF_FILE = "referrals.txt"
PREMIUM_FILE = "premium.txt"

for f in [USER_FILE, REF_FILE, PREMIUM_FILE]:
    if not os.path.exists(f):
        open(f, "w").close()

# 📌 tugma
keyboard = ReplyKeyboardMarkup(
    [["Qo‘shiq nomini yoz"]],
    resize_keyboard=True
)

# ================= PREMIUM SYSTEM =================

def add_ref(ref_id):
    with open(REF_FILE, "a") as f:
        f.write(f"{ref_id}\n")

def get_ref_count(ref_id):
    with open(REF_FILE, "r") as f:
        return f.read().splitlines().count(str(ref_id))

def make_premium(user_id):
    with open(PREMIUM_FILE, "a") as f:
        f.write(f"{user_id}\n")

def is_premium(user_id):
    with open(PREMIUM_FILE, "r") as f:
        return str(user_id) in f.read().splitlines()

# ================= START =================

@bot.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id

    # user saqlash
    with open(USER_FILE, "r") as f:
        users = set(f.read().splitlines())

    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(f"{user_id}\n")

    # ================= REFERRAL =================
    args = message.text.split()

    if len(args) > 1:
        ref_id = args[1]

        if ref_id != str(user_id) and ref_id != str(ADMIN_ID):
            add_ref(ref_id)

            count = get_ref_count(ref_id)

            # 🔥 5 TA ODAM → PREMIUM
            if count >= 5:
                make_premium(ref_id)

    # ADMIN CHECK
    if user_id == ADMIN_ID:
        admin_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("👁 Obunachilar", callback_data="check_subs")],
            [InlineKeyboardButton("📢 Xabar yuborish", callback_data="broadcast")]
        ])

        await message.reply(
            "👑 ADMIN PANEL",
            reply_markup=admin_buttons
        )
        return

    # USER START (HECH NARSA O'ZGARMAGAN)
    await message.reply_photo(
        photo="https://i.ibb.co/tpjt60kq/IMG-20260328-11432.jpg",
        caption="🎵 Salom men Azamat qo‘shiq nomini yoz 🎵",
        reply_markup=keyboard
    )

# ================= MUSIC =================

@bot.on_message(filters.text & ~filters.regex("^/"))
async def find_song(client, message):
    if message.text == "Qo‘shiq nomini yoz":
        await message.reply("🎶 Qo‘shiq yozing...")
        return

    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    loading = await message.reply_text("⏳ Qidirilyapti...")

    async def animate():
        while True:
            try:
                await loading.edit("⏳ Qidirilyapti...")
                await asyncio.sleep(1)
                await loading.edit("🔎 Kuting...")
                await asyncio.sleep(1)
                await loading.edit("🎧 Yuklanmoqda...")
                await asyncio.sleep(1)
            except:
                break

    task = asyncio.create_task(animate())

    query = message.text

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)

            if not info.get("entries"):
                task.cancel()
                await loading.edit("❌ Topilmadi!")
                return

            video = info['entries'][0]
            file_path = ydl.prepare_filename(video)

        task.cancel()
        await loading.edit("🎧 Tayyor...")

        await message.reply_audio(file_path, caption=video['title'])

        os.remove(file_path)
        await loading.delete()

    except Exception as e:
        task.cancel()
        print(e)
        await loading.edit("❌ Xatolik!")

# ================= ADMIN =================

@bot.on_callback_query(filters.regex("check_subs"))
async def check_subs(client, callback_query):
    if callback_query.from_user.id != ADMIN_ID:
        return

    with open(USER_FILE, "r") as f:
        users = len(f.read().splitlines())

    await callback_query.answer(f"👥 {users} user", show_alert=True)

@bot.on_callback_query(filters.regex("broadcast"))
async def broadcast(client, callback_query):
    if callback_query.from_user.id != ADMIN_ID:
        return

    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()

    for u in users:
        try:
            await client.send_message(int(u), "📢 Admin xabar!")
        except:
            pass

    await callback_query.answer("✅ Yuborildi", show_alert=True)

# ================= RUN =================
bot.run()
