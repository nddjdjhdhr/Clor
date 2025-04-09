import telebot
import requests
from bs4 import BeautifulSoup
import time

# === 🚀 Your Telegram Bot Token ===
API_TOKEN = '7704996444:AAEVPzoQn3EszCKriEru8A6DVEsyCWUSdXQ'
bot = telebot.TeleBot(API_TOKEN)

# === 👑 Your Telegram Admin ID ===
ADMIN_ID = 8179218740
OWNER_USERNAME = '@SIDIKI_MUSTAFA_47'

# === 📊 Win / Lose Tracking ===
win_count = 0
lose_count = 0
prediction_count = 0  # To track the number of predictions
pause_minutes = 3  # Default pause time in minutes
prediction_in_progress = False  # Flag to track ongoing prediction

# === 🔗 Required Telegram Channels ===
REQUIRED_CHANNELS = ['https://t.me/+GfSTkjSDTuhkOGI1', 'https://t.me/+MfPIKfWUpx1hZmJl']

# === 🔮 Smart Prediction Logic (Using Last 3 Digits) ===
def smart_predictor(last_three_digits):
    digits = [int(d) for d in str(last_three_digits)]
    total = sum(digits)
    last_digit = digits[-1]
    
    if last_digit in [8, 9, 7]:
        return "🔥 𝗕𝗶𝗴"
    elif last_digit in [0, 1, 2]:
        return "❄️ 𝗦𝗺𝗮𝗹𝗹"
    else:
        return "🔥 𝗕𝗶𝗴" if total % 10 > 4 else "❄️ 𝗦𝗺𝗮𝗹𝗹"

# === ✅ Check If User Joined Required Channels ===
def is_user_in_channels(user_id):
    for channel in REQUIRED_CHANNELS:
        chat_member = bot.get_chat_member(channel, user_id)
        if chat_member.status not in ['member', 'administrator', 'creator']:
            return False
    return True

# === 🎉 Start Command ===
@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.chat.id != ADMIN_ID:
        return
    
    if not is_user_in_channels(message.chat.id):
        bot.reply_to(message, f"⚠️ To use this bot, you must join the following channels:\n\n"
                              f"1️⃣ {REQUIRED_CHANNELS[0]}\n"
                              f"2️⃣ {REQUIRED_CHANNELS[1]}\n\n"
                              f"After joining, type /start again.")
        return
    
    start_text = (
        "🎉 *𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗦𝗠𝗔𝗥𝗧 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗢𝗥 𝗕𝗢𝗧!* 🎉\n\n"
        "🔹 𝗨𝘀𝗲 `/predict <last 3 digits>` 𝘁𝗼 𝗴𝗲𝘁 𝗮 𝗽𝗿𝗲𝗱𝗶𝗰𝘁𝗶𝗼𝗻.\n"
        "🔹 𝗖𝗵𝗲𝗰𝗸 𝘆𝗼𝘂𝗿 𝘀𝗰𝗼𝗿𝗲 𝘂𝘀𝗶𝗻𝗴 `/score`.\n"
        "🔹 𝗦𝗲𝗲 𝗮𝗹𝗹 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝘄𝗶𝘁𝗵 `/help`.\n\n"
        f"📸 𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗵𝗮𝗿𝗲 𝗮 𝗳𝗲𝗲𝗱𝗯𝗮𝗰𝗸 𝗽𝗵𝗼𝘁𝗼 𝘄𝗶𝘁𝗵 {OWNER_USERNAME} 𝗳𝗼𝗿 𝗮𝗻𝘆 𝘄𝗶𝗻𝘀!"
    )
    bot.reply_to(message, start_text, parse_mode="Markdown")

# === 📜 Help Command ===
@bot.message_handler(commands=['help'])
def handle_help(message):
    if message.chat.id != ADMIN_ID:
        return
    help_text = (
        "📜 *Available Commands:*\n"
        "🔹 `/predict <last 3 digits>` - 🔮 Get a prediction\n"
        "🔹 `/help` - 📜 Show this help menu\n"
        "🔹 `/score` - 📊 Show current win/loss count\n"
        "🔹 `/countdown <minutes>` - ⏳ Set pause time (Admin Only)\n"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

# === ⏳ Countdown Control Command ===
@bot.message_handler(commands=['countdown'])
def handle_countdown(message):
    global pause_minutes
    if message.chat.id != ADMIN_ID:
        return
    try:
        pause_minutes = int(message.text.split()[1])
        bot.reply_to(message, f"⏳ Pause time set to {pause_minutes} minutes.")
    except:
        bot.reply_to(message, "❌ Error: Use `/countdown <minutes>`")

# === 🔮 Prediction Command ===
@bot.message_handler(commands=['predict'])
def handle_predict(message):
    global win_count, lose_count, prediction_count, prediction_in_progress
    if message.chat.id != ADMIN_ID:
        return
    
    if prediction_in_progress:
        bot.reply_to(message, "⚠️ Please wait! Your previous prediction is still in progress.")
        return
    
    try:
        last_three_digits = int(message.text.split()[1])
        prediction = smart_predictor(last_three_digits)
        prediction_in_progress = True  # Set flag to indicate prediction is running
        actual_result = fetch_okwin_result()
        prediction_count += 1  # Increment prediction count

        if actual_result:
            if prediction.lower() == actual_result.lower():
                win_count += 1
                outcome = "✅ 𝗪𝗶𝗻"
                bot.send_message(ADMIN_ID, f"📸 𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗵𝗮𝗿𝗲 𝗮 𝗳𝗲𝗲𝗱𝗯𝗮𝗰𝗸 𝗽𝗵𝗼𝘁𝗼 𝘄𝗶𝘁𝗵 {OWNER_USERNAME}")
            else:
                lose_count += 1
                outcome = "❌ 𝗟𝗼𝘀𝘀"
        else:
            outcome = "⏳ 𝗥𝗲𝘀𝘂𝗹𝘁 𝗡𝗼𝘁 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗬𝗲𝘁"

        reply = f"🏆 𝗟𝗮𝘀𝘁 𝟯 𝗗𝗶𝗴𝗶𝘁𝘀: {last_three_digits}\n🔮 𝗣𝗿𝗲𝗱𝗶𝗰𝘁𝗶𝗼𝗻: {prediction}\n📊 𝗔𝗰𝘁𝘂𝗮𝗹 𝗥𝗲𝘀𝘂𝗹𝘁: {actual_result if actual_result else '𝗪𝗮𝗶𝘁𝗶𝗻𝗴...'}\n{outcome}\n🔢 𝗦𝗰𝗼𝗿𝗲: ✅ {win_count} | ❌ {lose_count}"
        bot.reply_to(message, reply)
        prediction_in_progress = False  # Reset flag after prediction is completed
    except:
        prediction_in_progress = False  # Reset flag in case of error
        bot.reply_to(message, "❌ 𝗘𝗿𝗿𝗼𝗿: 𝗨𝘀𝗲 `/predict <𝗹𝗮𝘀𝘁 𝟯 𝗱𝗶𝗴𝗶𝘁𝘀>`")

# === 🏆 Start the Bot ===
print("Bot is running...")
bot.polling()
