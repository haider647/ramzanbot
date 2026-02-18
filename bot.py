import os
import sqlite3
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# -------- Database Setup --------
try:
    conn = sqlite3.connect("users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        city TEXT
    )
    """)
    conn.commit()
except sqlite3.Error as e:
    print(f"Database Error: {e}")

# -------- Helper Functions --------
def get_prayer_times(city: str):
    """Fetch Fajr (Sehri) and Maghrib (Iftar) timings for Pakistan cities"""
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=Pakistan&method=2"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        timings = data.get("data", {}).get("timings", {})
        return timings.get("Fajr"), timings.get("Maghrib")
    except Exception as e:
        print(f"API Error for city '{city}': {e}")
        return None, None

def get_dates():
    """Return Gregorian and Hijri dates and current Ramadan day"""
    today = datetime.now()
    gregorian = today.strftime("%d-%m-%Y")
    try:
        url = f"http://api.aladhan.com/v1/gToH?date={today.strftime('%d-%m-%Y')}"
        response = requests.get(url, timeout=10).json()
        hijri_date = response["data"]["hijri"]["date"]
        day_of_ramadan = response["data"]["hijri"]["day"]
        return gregorian, hijri_date, int(day_of_ramadan)
    except:
        return gregorian, "N/A", "N/A"

# -------- /start Command --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gregorian, hijri, roza = get_dates()
    text = f"🌙 Ramzan Mubarak! 🌙\n\nToday: {gregorian} (Gregorian)\nIslamic: {hijri}\nRoza: {roza}\n\nSelect an option:"
    
    keyboard = [
        [InlineKeyboardButton("Sehri 🌙", callback_data="sehri")],
        [InlineKeyboardButton("Iftar 🌙", callback_data="iftar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await update.message.reply_text(text, reply_markup=reply_markup)
    except Exception as e:
        print(f"Error sending start message: {e}")

# -------- Callback Query Handler --------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data in ["sehri", "iftar"]:
        context.user_data["option"] = query.data
        await query.message.reply_text("Apni city type karein (e.g., Lahore, Karachi, Multan):")

# -------- Save City & Send Timing --------
async def save_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    user_id = update.effective_user.id

    try:
        cursor.execute("INSERT OR IGNORE INTO users(user_id) VALUES (?)", (user_id,))
        cursor.execute("UPDATE users SET city=? WHERE user_id=?", (city, user_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        await update.message.reply_text("❌ Database error occurred. Try again later.")
        return

    option = context.user_data.get("option")
    if option == "sehri":
        fajr, _ = get_prayer_times(city)
        if fajr:
            await update.message.reply_text(
                f"🌙 Aj apke {city} me Sehri ka time: {fajr} 🕓\n"
                "🤲 Roza rakhnay ki dua:\n"
                "وَبِصَوْمِ غَدٍ نَّوَيْتُ مِنْ شَهْرِ رَمَضَانَ 🌙"
            )
        else:
            await update.message.reply_text("❌ Timing fetch nahi ho paayi, phir try karein.")
    elif option == "iftar":
        _, maghrib = get_prayer_times(city)
        if maghrib:
            await update.message.reply_text(
                f"🌙 Aj apke {city} me Iftar ka time: {maghrib} 🕡\n"
                "🤲 Iftar ki dua:\n"
                "اَللّٰهُمَّ اِنِّی لَکَ صُمْتُ وَبِکَ اٰمَنْتُ وَعَلَيْکَ تَوَکَّلْتُ وَعَلٰی رِزْقِکَ اَفْطَرْتُ 🌙"
            )
        else:
            await update.message.reply_text("❌ Timing fetch nahi ho paayi, phir try karein.")
    else:
        await update.message.reply_text("❌ Please select Sehri or Iftar first using /start")

# -------- /dua Command --------
async def dua(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Ramzan Dua ✨\nاللهم إنك عفو تحب العفو فاعف عني 🤲🌙\n\nAllah aapko barkat aur sukoon ata farmaaye. Ameen."
    )

# -------- Main --------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Add Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_city))
app.add_handler(CommandHandler("dua", dua))

print("🌙 Ramzan Bot Running...")
app.run_polling()