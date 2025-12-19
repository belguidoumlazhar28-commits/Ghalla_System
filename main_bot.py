import os
import telebot
import time

TOKEN = os.getenv("BOT_TOKEN")

if TOKEN is None:
    print("ERROR: BOT_TOKEN not found")
    exit(1)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot is running 24/24 ✅")

print("Bot started...")

while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print("Polling error:", e)
        time.sleep(5)
