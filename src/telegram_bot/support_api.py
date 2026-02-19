import os
import requests

SUPPORT_BOT_TOKEN = os.getenv("TELEGRAM_SUPPORT_BOT_TOKEN")


def get_support_admin_ids() -> list[int]:
    admin_ids = os.getenv("SUPPORT_ADMIN_ID", "")
    if not admin_ids:
        return []
    return [int(x.strip()) for x in admin_ids.split(",") if x.strip()]



def send_support_message(title: str, name: str, phone: str, question: str = None):
    admin_ids = get_support_admin_ids()
    if not admin_ids:
        print("No SUPPORT_ADMIN_ID configured")
        return

    text = (
        f"{title}\n\n"
        f"👤 Імʼя: *{name}*\n"
        f"📞 Телефон: `{phone}`\n"
    )
    if question:
        text += f"❓ Питання: _{question}_\n"

    payload = {
        "text": text,
        "parse_mode": "Markdown",
    }

    url = f"https://api.telegram.org/bot{SUPPORT_BOT_TOKEN}/sendMessage"

    for admin_id in admin_ids:
        payload["chat_id"] = admin_id
        resp = requests.post(url, json=payload, timeout=10)
        if not resp.ok:
            print("Telegram SUPPORT send error:", resp.status_code, resp.text)
