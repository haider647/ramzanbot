import random
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "8568376187:AAGAm4ocyB-TyFiPUTBeTYArdBC9KadXbzw"

# -------------------- Ramadan Calendar --------------------
# Format: "DD-MM" : ("Suhoor", "Iftar")
CITIES_CALENDAR = {
    "Lahore": {
        "19-02": ("5:18 AM", "5:54 PM"), "20-02": ("5:17 AM", "5:54 PM"), # ... aur complete month
    },
    "Islamabad": {
        "19-02": ("5:24 AM", "5:56 PM"), "20-02": ("5:23 AM", "5:57 PM"),
    },
    "Rawalpindi": {
        "19-02": ("5:25 AM", "5:55 PM"), "20-02": ("5:24 AM", "5:56 PM"),
    },
    "Peshawar": {
        "19-02": ("5:31 AM", "6:01 PM"), "20-02": ("5:30 AM", "6:02 PM"),
    },
    "Gujranwala": {
        "19-02": ("5:20 AM", "5:52 PM"), "20-02": ("5:19 AM", "5:53 PM"),
    },
    "Multan": {
        "19-02": ("5:31 AM", "6:05 PM"), "20-02": ("5:30 AM", "6:06 PM"),
    },
    "Layyah": {},
    "Hafizabad": {},
    "Bahawalpur": {},
    "Pattoki": {},
    "Attock": {},
    "Karachi": {},
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

# -------------------- Keyboards --------------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌙 Sehri", callback_data="sehri")],
        [InlineKeyboardButton("🌇 Iftar", callback_data="iftar")]
    ])

def cities_menu(action):
    buttons = []
    for city in CITIES_CALENDAR.keys():
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
        today = datetime.now().strftime("%d-%m")
        calendar = CITIES_CALENDAR.get(city)
        if calendar is None or today not in calendar:
            await query.edit_message_text("⚠️ Timing fetch nahi ho paayi. Try later.")
            return

        sehri, iftar = calendar[today]
        time_value = sehri if action == "sehri" else iftar
        random_hadees = random.choice(HADEES_LIST)
        dua = SEHRI_DUA if action == "sehri" else IFTAR_DUA
        roza_number = list(calendar.keys()).index(today) + 1

        await query.edit_message_text(
            f"📍 *City:* {city}\n"
            f"📅 *Date:* {today}\n"
            f"⏰ *{action.capitalize()} Time:* {time_value}\n"
            f"Aj Ramzan ka ({roza_number}) roza hay\n\n"
            f"{dua}\n\n"
            f"{random_hadees}",
            parse_mode="Markdown"
        )

# -------------------- Setup --------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_trigger))
app.add_handler(CommandHandler("Ramzan", ramzan_cmd))
app.add_handler(CallbackQueryHandler(button_handler))

print("Bot started...")
app.run_polling()