import os
import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

# Replace with your bot token
BOT_TOKEN = '7653249811:AAFOiZyPE4COoEl3EcEQFOQvVdbePjCSsfg'

# Base URL to scrape and download
BASE_URL = 'https://udpcustom.online/slowdns-files/'

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Send /getfiles to receive all files from SlowDNS.")

def getfiles(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    update.message.reply_text("Fetching files, please wait...")

    try:
        # Scrape the page
        response = requests.get(BASE_URL)
        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a')
        file_links = [link.get('href') for link in links if link.get('href') and link.get('href').endswith('.txt') or link.get('href').endswith('.ovpn') or link.get('href').endswith('.udp') or link.get('href').endswith('.zip')]

        if not file_links:
            context.bot.send_message(chat_id=user_id, text="No downloadable files found.")
            return

        for file_link in file_links:
            file_url = BASE_URL + file_link
            file_response = requests.get(file_url)

            with open(file_link, 'wb') as f:
                f.write(file_response.content)

            with open(file_link, 'rb') as f:
                context.bot.send_document(chat_id=user_id, document=f)

            os.remove(file_link)

    except Exception as e:
        context.bot.send_message(chat_id=user_id, text=f"An error occurred: {e}")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("getfiles", getfiles))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
