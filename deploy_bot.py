import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# === 🔧 CONFIGURE THESE ===
BOT_TOKEN = "7653249811:AAFOiZyPE4COoEl3EcEQFOQvVdbePjCSsfg"  # Replace with your bot token
RAILWAY_API_TOKEN = "03f5e00c-7349-4449-811c-d9cb47e1b1a1"  # Replace with your Railway API token
PROJECT_ID = "03f5e00c-7349-4449-811c-d9cb47e1b1a1"  # Your Railway Project ID
ENVIRONMENT_ID = None  # Optional: only set if you have custom environments

# === 🛠️ Setup logging ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# === 🚀 START command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the KHAN-MD2 Deploy Bot!\n\n"
        "Send me your Telegram **session string** and I will deploy your userbot on Railway.\n\n"
        "⚠️ Your session string is private. Do not share it with anyone else."
    )


# === 📤 Handle session input ===
async def handle_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session_string = update.message.text.strip()

    if len(session_string) < 20 or "~" not in session_string:
        await update.message.reply_text("❌ This doesn't look like a valid session string.")
        return

    await update.message.reply_text("⏳ Deploying your userbot to Railway...")

    query = """
    mutation SetEnvironmentVariable($input: SetEnvironmentVariableInput!) {
        setEnvironmentVariable(input: $input) {
            environmentVariable {
                id
                key
                value
            }
        }
    }
    """

    variables = {
        "input": {
            "projectId": PROJECT_ID,
            "key": "SESSION_ID",
            "value": session_string
        }
    }

    if ENVIRONMENT_ID:
        variables["input"]["environmentId"] = ENVIRONMENT_ID

    headers = {
        "Authorization": f"Bearer {RAILWAY_API_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://backboard.railway.app/graphql",
        json={"query": query, "variables": variables},
        headers=headers
    )

    if response.status_code == 200 and "errors" not in response.json():
        await update.message.reply_text("✅ Userbot deployed successfully on Railway!")
    else:
        await update.message.reply_text("❌ Failed to deploy userbot.")
        logger.error("Railway API Error: %s", response.text)


# === 🤖 Launch the bot ===
if __name__ == "__main__":
    print("🤖 Starting Telegram Deploy Bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_session))

    app.run_polling()
