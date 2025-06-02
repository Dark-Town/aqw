import logging
import time
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Config
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
ADMIN_CHANNEL_ID = -1001234567890  # Replace with your channel ID
WELCOME_IMAGE_URL = 'https://example.com/welcome.jpg'  # URL of start image

logging.basicConfig(level=logging.INFO)

# Set up Selenium
def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)

# Scrape the tool site
def send_views(url: str) -> str:
    driver = get_driver()
    driver.get("https://myinstafollow.com/free-tiktok-views/")
    time.sleep(5)

    try:
        input_box = driver.find_element(By.NAME, "url")
        input_box.send_keys(url)

        submit = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
        submit.click()

        time.sleep(6)

        result = driver.find_element(By.CLASS_NAME, "result-area").text
    except Exception as e:
        result = f"Failed: {e}"
    finally:
        driver.quit()

    return result

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Send TikTok Views", callback_data='send_views')],
        [InlineKeyboardButton("ℹ️ About", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo=WELCOME_IMAGE_URL,
        caption="👋 Welcome! Use this bot to send free TikTok views.\nChoose an option below:",
        reply_markup=reply_markup
    )

# Button interactions
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'send_views':
        await query.message.reply_text("🔗 Please send your TikTok video link:")
        return
    elif query.data == 'about':
        await query.message.reply_text("⚡ This bot uses https://myinstafollow.com/free-tiktok-views to send views to TikTok videos.")

# Process TikTok link
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "tiktok.com" not in url:
        await update.message.reply_text("❌ Invalid TikTok URL. Please try again.")
        return

    await update.message.reply_text("⏳ Sending views... Please wait.")
    result = send_views(url)

    await update.message.reply_text(f"✅ Result:\n{result}")

    # Log to admin channel
    user = update.effective_user
    log_msg = f"👤 User: @{user.username or user.first_name}\n📹 TikTok: {url}\n🟢 Status: {result}"
    await context.bot.send_message(chat_id=ADMIN_CHANNEL_ID, text=log_msg)

# Main bot setup
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
