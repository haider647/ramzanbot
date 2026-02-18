from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
from datetime import datetime

# ====== Cities aur API mapping ======
CITIES = {
    "Lahore": "lahore",
    "Islamabad": "islamabad",
    "Karachi": "karachi",
    "Peshawar": "peshawar",
    "Rawalpindi": "rawalpindi",
    "Kahuta": "kahuta",
    "Multan": "multan",
    "Layyah": "layyah",
    "Hafizabad": "hafizabad",
    "Gujranwala": "gujranwala",
    "Bahawalpur": "bahawalpur",
    "Patoki": "patoki",
    "Attock": "attock"
}

# ====== Duas ======
DUA_SEHRI = "وَبِصَوْمِ غَدٍ نَّوَيْتُ مِنْ شَهْرِ رَمَضَانَ 🌙"
DUA_IFTAR = "اَللّٰهُمَّ اِنِّی لَکَ صُمْتُ وَبِکَ اٰمَنْتُ وَعَلَيْکَ تَوَکَّلْتُ وَعَلٰی رِزْقِکَ اَفْطَرْتُ 🌙"

# ====== Function: API se time fetch karna ======
def get_ramzan_time(city: str):
    try:
        response = requests.get(f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=Pakistan&method=2")
        data = response.json()
        timings = data['data']['timings']
        sehri_24 = timings['Fajr']
        iftar_24 = timings['Maghrib']
        # 12-hour format conversion
        sehri_12 = datetime.strptime(sehri_24, "%H:%M").strftime("%I:%M %p")
        iftar_12 = datetime.strptime(iftar_24, "%H:%M").strftime("%I:%M %p")
        return sehri_12, iftar_12
    except Exception as e:
        return None, None

# ====== Start command ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Sehri 🌙", callback_data="sehri")],
        [InlineKeyboardButton("Iftar 🌙", callback_data="iftar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Assalamualaikum! Sehri ya Iftar ka waqt janna chahte ho? 🌙", reply_markup=reply_markup)

# ====== Callback query ======
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data in ["sehri", "iftar"]:
        # City selection buttons
        keyboard = [[InlineKeyboardButton(city, callback_data=f"{query.data}|{city}")] for city in CITIES.keys()]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"City select karo 🌆 ({query.data.title()} time):", reply_markup=reply_markup)
    else:
        # Format: "sehri|Lahore"
        action, city = query.data.split("|")
        sehri_time, iftar_time = get_ramzan_time(CITIES[city])
        if action == "sehri":
            await query.edit_message_text(f"🌙 Sehri Time - {city}: {sehri_time}\nDua: {DUA_SEHRI}")
        else:
            await query.edit_message_text(f"🌙 Iftar Time - {city}: {iftar_time}\nDua: {DUA_IFTAR}")

# ====== Main ======
if __name__ == "__main__":
    BOT_TOKEN = "8568376187:AAGAm4ocyB-TyFiPUTBeTYArdBC9KadXbzw" #
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot is running...")
    app.run_polling()