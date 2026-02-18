import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8568376187:AAGAm4ocyB-TyFiPUTBeTYArdBC9KadXbzw"#

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cities = ["Karachi", "Lahore", "Islamabad", "Multan", "Peshawar"]
    keyboard = [[InlineKeyboardButton(city, callback_data=city)] for city in cities]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Apni city select karo:", reply_markup=reply_markup)

# Callback jab user city select kare
async def city_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city = query.data

    try:
        url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Pakistan&method=2"
        response = requests.get(url).json()

        sehri_time = response['data']['timings']['Fajr']
        iftar_time = response['data']['timings']['Maghrib']

        await query.edit_message_text(f"{city} ke liye timings:\n🌙 Sehri: {sehri_time}\n🌇 Iftar: {iftar_time}")
    except Exception as e:
        await query.edit_message_text(f"Error aaya: {e}\nShayad API ya city invalid hai.")

# Main function
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(city_selection))
    print("Bot chaloo ho gaya...")  # Logs ke liye
    app.run_polling()