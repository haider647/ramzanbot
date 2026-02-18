# bot.py
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from datetime import datetime
import pytz
import os

# 🔹 Bot Token (environment variable recommended)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# 🔹 Pakistan Cities
CITIES = [
    "Karachi","Lahore","Islamabad","Faisalabad","Multan","Quetta","Peshawar",
    "Sialkot","Gujranwala","Bahawalpur","Hafizabad","Attock","Layyah"
]

# 🔹 Roza Duas
SEHRI_DUA = "وَبِصَوْمِ غَدٍ نَّوَيْتُ مِنْ شَهْرِ رَمَضَانَ 🌙"
IFTAR_DUA = "اَللّٰهُمَّ اِنِّی لَکَ صُمْتُ وَبِکَ اٰمَنْتُ وَعَلَيْکَ تَوَکَّلْتُ وَعَلٰی رِزْقِکَ اَفْطَرْتُ 🌙🍴"

# 🔹 Function to fetch Sehri/Iftar times
def get_times(city):
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=Pakistan&method=2"
        response = requests.get(url)
        data = response.json()
        sehri = data["data"]["timings"]["Fajr"]
        iftar = data["data"]["timings"]["Maghrib"]
        return sehri, iftar
    except Exception as e:
        print(f"Error fetching times: {e}")
        return None, None

# 🔹 Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today_gregorian = datetime.now(pytz.timezone("Asia/Karachi")).strftime("%d-%m-%Y")
    today_hijri = requests.get("https://api.aladhan.com/v1/gToH?date="+today_gregorian).json()["data"]["date"]["hijri"]["date"]
    
    keyboard = [
        [InlineKeyboardButton("🌙 Sehri", callback_data="sehri")],
        [InlineKeyboardButton("🍴 Iftar", callback_data="iftar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🌙 Ramzan Mubarak! ✨\n\nAj ka roza:\nGregorian: {today_gregorian}\nHijri: {today_hijri}",
        reply_markup=reply_markup
    )

# 🔹 Callback for buttons
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "sehri":
        await query.message.reply_text("Apni city type karein: " + ", ".join(CITIES))
        context.user_data["mode"] = "sehri"
    elif query.data == "iftar":
        await query.message.reply_text("Apni city type karein: " + ", ".join(CITIES))
        context.user_data["mode"] = "iftar"

# 🔹 Message handler for city
async def city_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    mode = context.user_data.get("mode", "")
    
    if city not in CITIES:
        await update.message.reply_text("❌ Invalid city! Try again.")
        return
    
    sehri, iftar = get_times(city)
    if not sehri or not iftar:
        await update.message.reply_text("⚠️ Timing fetch nahi ho saki. Thodi der baad try karein.")
        return
    
    if mode == "sehri":
        await update.message.reply_text(f"🌙 Aj apke {city} me Sehri ka time: {sehri}\n\nDua: {SEHRI_DUA}")
    elif mode == "iftar":
        await update.message.reply_text(f"🍴 Aj apke {city} me Iftar ka time: {iftar}\n\nDua: {IFTAR_DUA}")
    else:
        await update.message.reply_text("❌ Pehle Sehri ya Iftar select karein.")

# 🔹 Main App
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, city_handler))

# 🔹 Run bot
app.run_polling()
