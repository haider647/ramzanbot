from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import requests
from datetime import datetime

# ===== Cities =====
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

# ===== Duas =====
DUA_SEHRI = "🌙✨ **Dua for Sehri:** وَبِصَوْمِ غَدٍ نَّوَيْتُ مِنْ شَهْرِ رَمَضَانَ"
DUA_IFTAR = "🌅✨ **Dua for Iftar:** اَللّٰهُمَّ اِنِّی لَکَ صُمْتُ وَبِکَ اٰمَنْتُ وَعَلَيْکَ تَوَکَّلْتُ وَعَلٰی رِزْقِکَ اَفْطَرْتُ"

# ===== Fetch Sehri/Iftar time =====
def get_ramzan_time(city: str):
    try:
        res = requests.get(f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=Pakistan&method=2")
        data = res.json()['data']['timings']
        sehri_12 = datetime.strptime(data['Fajr'], "%H:%M").strftime("%I:%M %p")
        iftar_12 = datetime.strptime(data['Maghrib'], "%H:%M").strftime("%I:%M %p")
        return sehri_12, iftar_12
    except:
        return None, None

# ===== Ramazan trigger =====
async def ramazan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌙 Sehri", callback_data="sehri")],
        [InlineKeyboardButton("🌅 Iftar", callback_data="iftar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌟 **Assalamualaikum! Ramzan ke Sehri aur Iftar timings janna chahte ho?** 🌙\n\n"
        "Neeche buttons par click karo:", reply_markup=reply_markup
    )

# ===== Callback query =====
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data in ["sehri", "iftar"]:
        keyboard = []
        row = []
        for idx, city in enumerate(CITIES.keys(), 1):
            row.append(InlineKeyboardButton(city, callback_data=f"{query.data}|{city}"))
            if idx % 2 == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        await query.edit_message_text(
            f"🏙️ **City select karo ({query.data.title()} time):**", 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        action, city = query.data.split("|")
        sehri_time, iftar_time = get_ramzan_time(CITIES[city])
        if action == "sehri":
            await query.edit_message_text(f"🌙 **Sehri time for {city}: {sehri_time}**\n\n{DUA_SEHRI}")
        else:
            await query.edit_message_text(f"🌅 **Iftar time for {city}: {iftar_time}**\n\n{DUA_IFTAR}")

# ===== Main =====
BOT_TOKEN = "8568376187:AAGAm4ocyB-TyFiPUTBeTYArdBC9KadXbzw"

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Message without slash trigger
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.Regex("^Ramazan$"), ramazan))
app.add_handler(CallbackQueryHandler(button))

print("💫 Ramzan bot chaloo hai...")

app.run_polling()