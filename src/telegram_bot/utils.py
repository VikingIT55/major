from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def send_order(chat_id: int, message: str, customer_first_name: str, customer_last_name: str, reference: str, app):
    keyboard = [[InlineKeyboardButton("✅ Відправлено", callback_data=f"mark_done|{customer_first_name}|{customer_last_name}|{reference}"),
                 InlineKeyboardButton("❌ Скасувати", callback_data=f"cancel_order|{customer_first_name}|{customer_last_name}|{reference}")]]
    markup = InlineKeyboardMarkup(keyboard)
    await app.bot.send_message(chat_id=chat_id, text=message, reply_markup=markup, parse_mode="Markdown")
