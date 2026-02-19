import os

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv

from telegram_bot.handlers import start_command, button_handler


load_dotenv()

SHOP_BOT_TOKEN = os.getenv("TELEGRAM_SHOP_BOT_TOKEN")


def run_bot():
    app = ApplicationBuilder().token(SHOP_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    run_bot()
