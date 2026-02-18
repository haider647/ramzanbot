
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# --------- Cities aur API Key ---------
cities = {
    "Lahore": {"lat": 31.5204, "lon": 74.3587},
    "Islamabad": {"lat": 33.6844, "lon": 73.0479},
    "Karachi": {"lat": 24.8607, "lon": 67.0011},
    "Peshawar": {"lat": 34.0151, "lon": 71.5249},
    "Rawalpindi": {"lat": 33.5651, "lon": 73.0169},
    "Kahuta": {"lat": 33.6063, "lon": 73.3874},
    "Multan": {"lat": 30.1575, "lon": 71.5249},
    "Layyah": {"lat": 30.9610, "lon": 70.9325},
    "Hafizabad": {"lat": 32.0700, "lon": 73.6851},
    "Gujranwala": {"lat": 32.1877, "lon": 74.1945},
    "Bahawalpur": {"lat": 29.3956, "lon": 71.6836},
    "Patoki": {"lat": 31.0200, "lon": 73.9940},
    "Attock": {"lat": 33.7680, "lon": 72.3600}
}

duas = {
    "sehri": "🤲 **Allahumma inni laka sumtu wa bika aamantu wa 'alayka tawakkaltu**",
    "iftar": "🤲 **Allahumma inni laka sumtu wa bika aamantu wa 'alayka tawakkaltu, wa 'ala rizq-ika-aftartu**"
}

# --------- Function to get daily timings from Aladhan API ---------
def get_times(lat, lon):
    url = f"http://api.aladhan.com/v1/timingsToday?latitude={lat}&longitude={lon}&method=2"
    try:
        response = requests.get(url).json()
        timings = response["data"]["timings"]
        # Convert 24h to 12h format
        sehri = datetime.strptime(timings["Fajr"], "%H:%M").strftime("%I:%M %p")
        iftar = datetime.strptime(timings["Maghrib"], "%H:%M").strftime("%I:%M %p")
        return sehri, iftar
    except:
        return "Error", "Error"

# --------- Ramzan Command / Message ---------
async def ramzan_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌙 Sehri", callback_data="sehri")],
        [InlineKeyboardButton("🌇 Iftar", callback_data="iftar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✨ **Assalamualaikum! Ramzan Mubarak!** ✨\n\n"
        "Aap ko Sehri ya Iftar ka waqt dekhna hai? 👇", 
        reply_markup=reply_markup, parse_mode="Markdown"
    )

# --------- Callback for City Selection ---------
async def city_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    action = query.data  # 'sehri' ya 'iftar'
    
    keyboard = [[InlineKeyboardButton(city, callback_data=f"{action}|{city}")] for city in cities.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🌐 **Cities** - Select for {action.capitalize()} time ⏰", 
        reply_markup=reply_markup, parse_mode="Markdown"
    )

# --------- Callback for Time & Dua ---------
async def show_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    action, city = query.data.split("|")
    lat, lon = cities[city]["lat"], cities[city]["lon"]
    sehri, iftar = get_times(lat, lon)
    
    time = sehri if action == "sehri" else iftar
    dua_text = duas[action]
    
    await query.edit_message_text(
        f"📍 **City:** {city}\n"
        f"⏰ **{action.capitalize()} Time:** {time}\n\n"
        f"{dua_text}",
        parse_mode="Markdown"
    )

# --------- Main Bot Setup ---------
app = ApplicationBuilder().token("8568376187:AAGAm4ocyB-TyFiPUTBeTYArdBC9KadXbzw").build()

# "Ramzan" type karne se trigger
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.Regex(r'(?i)^Ramzan$'), ramzan_message))
app.add_handler(CallbackQueryHandler(city_selection, pattern="^(sehri|iftar)$"))
app.add_handler(CallbackQueryHandler(show_time, pattern="^(sehri|iftar)\|"))

print("🤖 Ramzan Bot is running...")
app.run_polling()