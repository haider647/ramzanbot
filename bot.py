
import requests
import random
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

TOKEN = "8568376187:AAGAm4ocyB-TyFiPUTBeTYArdBC9KadXbzw"

CITIES = ["Lahore", "Karachi", "Islamabad", "Peshawar"]

HADEES = [
    "📖 Roza dhaal hai. — Bukhari",
    "📖 Roza aur Quran shafa'at karenge. — Ahmad",
    "📖 Imaan ke saath roza rakhne walay ke gunaah maaf hote hain. — Bukhari"
]

SEHRI_DUA = "🤲 Sehri Dua: Wa bisawmi ghadin nawaiytu..."
IFTAR_DUA = "🤲 Iftar Dua: Allahumma inni laka sumtu..."

# -------- API ----------
def get_time(city):
    try:
        url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Pakistan&method=2"
        r = requests.get(url, timeout=8).json()
        t = r["data"]["timings"]
        sehri = datetime.strptime(t["Fajr"], "%H:%M").strftime("%I:%M %p")
        iftar = datetime.strptime(t["Maghrib"], "%H:%M").strftime("%I:%M %p")
        return sehri, iftar
    except:
        return None, None

# -------- Start ----------
async def ramzan(update, context):
    kb = [
        [InlineKeyboardButton("🌙 Sehri", callback_data="sehri")],
        [InlineKeyboardButton("🌇 Iftar", callback_data="iftar")]
    ]
    await update.message.reply_text(
        "Ramzan Mubarak 🌙\nSelect option:",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# -------- Buttons ----------
async def buttons(update, context):
    q = update.callback_query
    await q.answer()

    if q.data in ["sehri", "iftar"]:
        kb = [[InlineKeyboardButton(c, callback_data=f"{q.data}|{c}")] for c in CITIES]
        await q.edit_message_text(
            "Select City:",
            reply_markup=InlineKeyboardMarkup(kb)
        )
    else:
        action, city = q.data.split("|")
        sehri, iftar = get_time(city)

        if not sehri:
            await q.edit_message_text("Error fetching time. Try again.")
            return

        time_val = sehri if action == "sehri" else iftar
        dua = SEHRI_DUA if action == "sehri" else IFTAR_DUA
        hadees = random.choice(HADEES)

        await q.edit_message_text(
            f"📍 {city}\n"
            f"⏰ {action.capitalize()} Time: {time_val}\n\n"
            f"{dua}\n\n"
            f"{hadees}"
        )

# -------- Run ----------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("Ramzan", ramzan))
app.add_handler(CallbackQueryHandler(buttons))
app.run_polling()