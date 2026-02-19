import os
import json
import requests


BOT_TOKEN = os.getenv("TELEGRAM_SHOP_BOT_TOKEN")

def send_order_to_admin(chat_id: int, message: str, 
                        customer_first_name: str, customer_last_name: str,
                        reference: str) -> None:
    
    keyboard = [[
        {
            "text": "✅ Відправлено",
            "callback_data": f"mark_done|{customer_first_name}|{customer_last_name}|{reference}",
        },
        {
            "text": "❌ Скасувати",
            "callback_data": f"cancel_order|{customer_first_name}|{customer_last_name}|{reference}",
        },
    ]]

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps({"inline_keyboard": keyboard}),
    }

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    respesonse = requests.post(url, json=payload, timeout=10)

    if not respesonse.ok:
        print("Telegram API error:", respesonse.status_code, respesonse.text)