
import requests
import random
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "8568376187:AAGAm4ocyB-TyFiPUTBeTYArdBC9KadXbzw"

# -------------------- Cities --------------------
CITIES = {
    "Lahore": {"city": "Lahore", "country": "Pakistan"},
    "Islamabad": {"city": "Islamabad", "country": "Pakistan"},
    "Karachi": {"city": "Karachi", "country": "Pakistan"},
    "Peshawar": {"city": "Peshawar", "country": "Pakistan"},
    "Rawalpindi": {"city": "Rawalpindi", "country": "Pakistan"},
    "Kahuta": {"city": "Kahuta", "country": "Pakistan"},
    "Multan": {"city": "Multan", "country": "Pakistan"},
    "Layyah": {"city": "Layyah", "country": "Pakistan"},
    "Hafizabad": {"city": "Hafizabad", "country": "Pakistan"},
    "Gujranwala": {"city": "Gujranwala", "country": "Pakistan"},
    "Bahawalpur": {"city": "Bahawalpur", "country": "Pakistan"},
    "Patoki": {"city": "Patoki", "country": "Pakistan"},
    "Attock": {"city": "Attock", "country": "Pakistan"}
}

# -------------------- Duas --------------------
SEHRI_DUA = "🤲 *Sehri Dua:* وَبِصَوْمِ غَدٍ نَّوَيْتُ مِنْ شَهْرِ رَمَضَانَ"
IFTAR_DUA = "🤲 *Iftar Dua:* اَللّٰهُمَّ اِنِّی لَکَ صُمْتُ وَبِکَ اٰمَنْتُ وَعَلَيْکَ تَوَکَّلْتُ وَعَلٰی رِزْقِکَ اَفْطَرْتُ"

# -------------------- Random Hadees --------------------
HADEES_LIST = [
    "📖 *Hadees:* الصوم جنة (Roza dhaal hai). — Sahih Bukhari",
    "📖 *Hadees:* Jo shakhs imaan ke saath aur sawab ki niyyat se roza rakhe, uske pichle gunaah maaf kar diye jate hain. — Sahih Bukhari",
    "📖 *Hadees:* Roza aur Quran qiyamat ke din shafa'at karenge. — Musnad Ahmad",
    "📖 *Hadees:* Roza daar ke liye do khushiyan hain: ek iftar ke waqt aur ek apne Rab se mulaqat ke waqt. — Sahih Muslim"
]

# -------------------- API Function --------------------
def fetch_times(city, country):
    try:
        url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=2&school=1"
        response = requests.get(url, timeout=10).json()
        times = response["data"]["timings"]

        sehri = datetime.strptime(times["Fajr"], "%H:%M").strftime("%I:%M %p")
        iftar = datetime.strptime(times["Maghrib"], "%H:%M").strftime("%I:%M %p")

        return sehri, iftar
    except Exception as e:
        print(f"Error fetching times for {city}: {e}")
        return None, None

# -------------------- Keyboards --------------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌙 Sehri", callback_data="sehri")],
        [InlineKeyboardButton("🌇 Iftar", callback_data="iftar")]
    ])

def cities_menu(action):
    buttons = []
    for city in CITIES.keys():
        buttons.append([InlineKeyboardButton(city, callback_data=f"{action}|{city}")])
    return InlineKeyboardMarkup(buttons)

# -------------------- Handlers --------------------
async def ramzan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 *Ramzan Mubarak!*\n\nSehri ya Iftar time dekhna hai?",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

async def text_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == "ramzan":
        await ramzan_cmd(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in ["sehri", "iftar"]:
        await query.edit_message_text(
            "📍 *Apni city select karein:*",
            reply_markup=cities_menu(data),
            parse_mode="Markdown"
        )
    else:
        action, city = data.split("|")
        city_info = CITIES.get(city)

        sehri, iftar = fetch_times(city_info["city"], city_info["country"])
        if sehri is None:
            await query.edit_message_text("⚠️ Timing fetch nahi ho paayi. Try later.")
            return

        random_hadees = random.choice(HADEES_LIST)
        dua = SEHRI_DUA if action == "sehri" else IFTAR_DUA
        time_value = sehri if action == "sehri" else iftar

        await query.edit_message_text(
            f"📍 *City:* {city}\n"
            f"⏰ *{action.capitalize()} Time:* {time_value}\n\n"
            f"{dua}\n\n"
            f"{random_hadees}",
            parse_mode="Markdown"
        )

# -------------------- Setup --------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_trigger))
app.add_handler(CallbackQueryHandler(button_handler))

print("Bot started...")
app.run_polling()