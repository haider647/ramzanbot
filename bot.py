import os
import sqlite3
import requests
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================= DATABASE =================
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    city TEXT
)
""")
conn.commit()

# ================= CITIES =================
CITIES = ["Karachi", "Lahore", "Islamabad", "Multan", "Peshawar", "Quetta"]

# ================= API =================
def get_times(city):
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=Pakistan&method=2"
        response = requests.get(url, timeout=5).json()

        fajr = response["data"]["timings"]["Fajr"]
        maghrib = response["data"]["timings"]["Maghrib"]
        return fajr, maghrib

    except Exception as e:
        print("API Error:", e)
        return None, None

# ================= COMMANDS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    keyboard = [[city] for city in CITIES]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "🌙 Ramzan Mubarak! 🌙\n\nApni city select karein taake Sehri & Iftar reminders mil sakein 🕌⏰",
        reply_markup=reply_markup
    )

async def setcity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    user_id = update.effective_user.id

    if city not in CITIES:
        await update.message.reply_text("❌ Please list me se city select karein.")
        return

    cursor.execute("UPDATE users SET city=? WHERE user_id=?", (city, user_id))
    conn.commit()

    await update.message.reply_text(f"✅ City set ho gayi: {city} 🌆")

async def sehri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT city FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if not result or not result[0]:
        await update.message.reply_text("❌ Pehle /start karein aur city select karein.")
        return

    city = result[0]
    fajr, _ = get_times(city)

    if not fajr:
        await update.message.reply_text("⚠ API se time fetch nahi ho saka. Baad mein try karein.")
        return

    await update.message.reply_text(
        f"🌙 Sehri Time 🌙\n\nCity: {city}\nSehri (Fajr): {fajr} 🕓\n\n🥣 Time pe uthna mat bhoolna!"
    )

async def iftar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT city FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if not result or not result[0]:
        await update.message.reply_text("❌ Pehle /start karein aur city select karein.")
        return

    city = result[0]
    _, maghrib = get_times(city)

    if not maghrib:
        await update.message.reply_text("⚠ API se time fetch nahi ho saka. Baad mein try karein.")
        return

    await update.message.reply_text(
        f"🌙 Iftar Time 🌙\n\nCity: {city}\nIftar (Maghrib): {maghrib} 🕡\n\n🍽️ Dua ke saath roza kholein!"
    )

async def dua(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Ramzan Dua ✨\n\nاللهم إنك عفو تحب العفو فاعف عني 🤲🌙\n\nAllah aapko barkat aur sukoon ata farmaaye. Ameen."
    )

# ================= AUTO REMINDER =================

async def auto_reminder(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%H:%M")

    cursor.execute("SELECT user_id, city FROM users WHERE city IS NOT NULL")
    users = cursor.fetchall()

    for user_id, city in users:
        fajr, maghrib = get_times(city)

        if not fajr or not maghrib:
            continue

        if now == fajr:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🌙 Sehri Reminder 🌙\nCity: {city}\nTime: {fajr} 🕓🥣"
            )

        if now == maghrib:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🌙 Iftar Reminder 🌙\nCity: {city}\nTime: {maghrib} 🕡🍽️"
            )

# ================= MAIN =================

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("sehri", sehri))
app.add_handler(CommandHandler("iftar", iftar))
app.add_handler(CommandHandler("dua", dua))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, setcity))

app.job_queue.run_repeating(auto_reminder, interval=60, first=10)

print("🌙 Ramzan Bot Running...")
app.run_polling()
