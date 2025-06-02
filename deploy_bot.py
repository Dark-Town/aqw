import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram Bot Token
BOT_TOKEN = '7653249811:AAFOiZyPE4COoEl3EcEQFOQvVdbePjCSsfg'

# Selenium Setup (Headless Chrome)
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver

# Scraping Function
def fetch_tool_info(url: str) -> str:
    driver = get_driver()
    driver.get("https://myinstafollow.com/free-tiktok-tools")
    time.sleep(5)  # Let the page load

    try:
        # Example interaction: Locate input field and submit URL (customize this for your tool's logic)
        input_box = driver.find_element(By.NAME, "url")
        input_box.send_keys(url)

        submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
        submit_btn.click()

        time.sleep(5)  # Wait for results

        # Grab the output text (adjust the selector to fit real result container)
        result = driver.find_element(By.CLASS_NAME, "result-area").text
    except Exception as e:
        result = f"Error while scraping: {str(e)}"
    finally:
        driver.quit()

    return result

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a TikTok video URL, and I'll fetch info using Free TikTok Tools!")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_url = update.message.text
    await update.message.reply_text("Fetching info, please wait...")
    result = fetch_tool_info(user_url)
    await update.message.reply_text(result)

# Main Bot Setup
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.run_polling()

if __name__ == "__main__":
    main()
