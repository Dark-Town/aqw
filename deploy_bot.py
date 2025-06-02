import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler, ContextTypes
)
from playwright.async_api import async_playwright

# CONFIG
BOT_TOKEN = '653249811:AAFOiZyPE4COoEl3EcEQFOQvVdbePjCSsfg'
LOG_CHANNEL_ID = -1001234567890  # Replace with your channel ID
ASK_URL = 1

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Playwright automation ---
async def send_views_to_tiktok(url: str) -> bool:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://myinstafollow.com/free-tiktok-views/", timeout=60000)

            await page.fill("input[name='url']", url)
            await page.click("button[type='submit']")

            await page.wait_for_timeout(5000)
            html = await page.content()

            await browser.close()
            return "success" in html.lower() or "views have been sent" in html.lower()
    except Exception as e:
        logger.error(f"Automation error: {e}")
        return False


# --- Telegram Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Get TikTok Views", callback_data="get_views")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Welcome!\nUse the button below to get free TikTok views.",
        reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_views":
        await query.message.reply_text("📥 Send your TikTok video URL:")
        return ASK_URL

    elif query.data == "about":
        await query.message.reply_text("🤖 This bot sends TikTok views using myinstafollow.com")
        return ConversationHandler.END


async def receive_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    tiktok_url = update.message.text

    if "tiktok.com" not in tiktok_url:
        await update.message.reply_text("❌ That doesn't look like a valid TikTok link.")
        return ASK_URL

    await update.message.reply_text("⏳ Sending views... Please wait...")

    success = await send_views_to_tiktok(tiktok_url)

    if success:
        await update.message.reply_text("✅ Views sent successfully!")
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=f"✅ {user.full_name} (@{user.username or 'NoUsername'}) received views for:\n{tiktok_url}"
        )
    else:
        await update.message.reply_text("❌ Failed to send views. Try again later.")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling update:", exc_info=context.error)


# --- Main Function ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={ASK_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_url)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_error_handler(error_handler)

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
