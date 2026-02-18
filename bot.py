import asyncio
from datetime import datetime, timedelta
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# -------------------------------
# CONFIG
# -------------------------------
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Pakistan cities with timezone offset
CITIES = {
    "Karachi": "Asia/Karachi",
    "Lahore": "Asia/Karachi",
    "Islamabad": "Asia/Karachi",
    "Multan": "Asia/Karachi",
    "Faisalabad": "Asia/Karachi",
    "Gujranwala": "Asia/Karachi",
    "Bahawalpur": "Asia/Karachi",
    "Attock": "Asia/Karachi",
    "Hafizabad": "Asia/Karachi",
    "Layyah": "Asia/Karachi"
}

# Sehri & Iftar duas
SEHRI_DUA = "وَبِصَوْمِ غَدٍ نَّوَيْتُ مِنْ شَهْرِ رَمَضَانَ"
IFTAR_DUA = "اَللّٰهُمَّ اِنِّی لَکَ صُمْتُ وَبِکَ اٰمَنْتُ وَعَلَيْکَ تَوَکَّلْتُ وَعَلٰی رِزْقِکَ اَفْطَرْتُ"

# Placeholder Ramzan schedule (sample, normally you fetch real timings)
# Format: "HH:MM" in 24hr format
RAMZAN_TIMINGS = {
    "Karachi": {"sehri": "04:30", "iftar": "18:50"},
    "Lahore": {"sehri": "04:35", "iftar": "18:55"},
    "Islamabad": {"sehri": "04:32", "iftar": "18:52"},
    "Multan": {"sehri": "04:34", "iftar": "18:54"},
    "Faisalabad": {"sehri": "04:33", "iftar": "18:53"},
    "Gujranwala": {"sehri": "04:33", "iftar": "18:53"},
    "Bahawalpur": {"sehri": "04:36", "iftar": "18:56"},
    "Attock": {"sehri": "04:31", "iftar": "18:51"},
    "Hafizabad": {"sehri": "04:33", "iftar": "18:53"},
    "Layyah": {"sehri": "04:35", "iftar": "18:55"}
}

# -------------------------------
# HELPERS
# -------------------------------
def get_today_info():
    # Gregorian date
    now = datetime.now(pytz.timezone("Asia/Karachi"))
    gregorian = now.strftime("%d-%m-%Y")

    # Simple roza count (1-30)
    ramzan_start = datetime(now.year, 4, 2, tzinfo=pytz.timezone("Asia/Karachi"))  # Example start date
    day_num = (now - ramzan_start).days + 1
    day_num = max(1, min(day_num, 30))  # Clamp 1-30

    # Islamic date (simplified, just for display)
    hijri_day = day_num
    hijri_month = "Ramzan"

    return f"📅 Gregorian: {gregorian}\n🕌 Islamic: {hijri_day} {hijri_month}\n🌙 Today: Roza {day_num}"

def get_timing(city: str, action: str):
    if city not in RAMZAN_TIMINGS:
        return "City not found!"
    time = RAMZAN_TIMINGS[city][action]
    dua = SEHRI_DUA if action == "sehri" else IFTAR_DUA
    emoji = "🌄" if action == "sehri" else "🌇"
    return f"{emoji} {action.title()} time in {city}: {time}\n🙏 Dua:\n{dua}"

# -------------------------------
# HANDLERS
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"✨ Ramzan Mubarak! ✨\n\n{get_today_info()}"
    keyboard = [
        [InlineKeyboardButton("Sehri 🌄", callback_data="sehri")],
        [InlineKeyboardButton("Iftar 🌇", callback_data="iftar")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data  # 'sehri' or 'iftar'
    keyboard = [[InlineKeyboardButton(city, callback_data=f"{action}|{city}")] for city in CITIES]
    await query.edit_message_text(f"Select your city for {action.title()} time:", reply_markup=InlineKeyboardMarkup(keyboard))

async def city_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("|")
    action, city = data[0], data[1]
    result = get_timing(city, action)
    await query.edit_message_text(result)

# -------------------------------
# MAIN
# -------------------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(city_selection, pattern="^(sehri|iftar)\|"))
app.add_handler(CallbackQueryHandler(button, pattern="^(sehri|iftar)$"))

app.run_polling()