import os

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv

from telegram_bot.handlers import (
    start_command_support, 
    button_handler, 
    support_message_handler, 
    reply_command, 
    faq_callback_handler
)


load_dotenv()

SUPPORT_BOT_TOKEN = os.getenv("TELEGRAM_SUPPORT_BOT_TOKEN")


def run_bot():
    app = ApplicationBuilder().token(SUPPORT_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command_support))
    app.add_handler(CallbackQueryHandler(faq_callback_handler, pattern=r"^faq_"))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, support_message_handler))
    app.add_handler(CommandHandler("reply", reply_command))
    app.run_polling()

if __name__ == "__main__":
    run_bot()
