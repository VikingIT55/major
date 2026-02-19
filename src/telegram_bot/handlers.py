import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Привіт! Надішли замовлення через сайт - https://major-gamma.vercel.app/")
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Привіт! Надішли замовлення через сайт - https://major-gamma.vercel.app/"
        )

async def start_command_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("❓ Як замовити", callback_data="faq_order"),
            InlineKeyboardButton("🚚 Доставка", callback_data="faq_delivery")
        ],
        [
            InlineKeyboardButton("💳 Оплата", callback_data="faq_payment"),
            InlineKeyboardButton("📦 Повернення", callback_data="faq_return")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привіт! Обери запитання нижче, або напиши своє звернення.",
        reply_markup=markup
    )

async def faq_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "faq_order":
        await query.message.reply_text("📦 Щоб замовити, додайте товари в кошик і натисніть 'Оформити'.")
    elif data == "faq_delivery":
        await query.message.reply_text("🚚 Ми доставляємо Новою Поштою протягом 1–2 днів.")
    elif data == "faq_payment":
        await query.message.reply_text("💳 Оплата можлива Monobank Pay, або післяплатою.")
    elif data == "faq_return":
        await query.message.reply_text("📦 Повернення товарів можливе протягом 14 днів за рахунок покупця.")

            


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data or "|" not in query.data:
        await query.message.reply_text("⚠️ Невідома дія.")
        return

    
    parts = query.data.split("|")

    if parts[0] in ["mark_done", "cancel_order"] and len(parts) == 4:

        action, name, last_name, reference = parts[0], parts[1], parts[2], parts[3]  

        await query.edit_message_reply_markup(reply_markup=None)

        if action == "mark_done":
            await query.message.reply_text(
                f"✅ Замовлення №{reference} для *{name} {last_name}* виконано 🙂!\n",
                parse_mode="Markdown"
            )

        elif action == "cancel_order":
            await query.message.reply_text(
                f"❌ Замовлення №{reference} для *{name} {last_name}* було скасовано 😢",
                parse_mode="Markdown"
            )

    elif parts[0] in ["close_support", "reply_to_user"] and len(parts) == 2:

        action, name = parts[0], parts[1]

        await query.edit_message_reply_markup(reply_markup=None)

        if action == "close_support":
            await query.message.reply_text(
                f"✅ Звернення від користувача `{name}` закрито.",
                parse_mode="Markdown"
            )
        elif action == "reply_to_user":
            await query.message.reply_text(
                f"✏️ Щоб відповісти користувачу, надішліть:\n/reply {name} <ваше повідомлення>",
                parse_mode="Markdown"
            )
    else:
        await query.message.reply_text("⚠️ Невідома команда.")

def get_admin_ids(env_var_name: str = "SUPPORT_ADMIN_ID") -> list[int]:
    admin_ids = os.getenv(env_var_name, "")
    if not admin_ids:
        return []
    try:
        return [int(x.strip()) for x in admin_ids.split(",") if x.strip()]
    except ValueError as e:
        print(f"Некоректне значення в SUPPORT_ADMIN_ID: {e}")
        return []

async def support_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user = update.effective_user
    text = update.message.text or ""
    chat_id = update.effective_chat.id

    admin_ids = get_admin_ids()
    if not admin_ids:
        await update.message.reply_text("⚠️ Немає налаштованих адміністраторів. Додай SUPPORT_ADMIN_ID у .env")
        return
    
    name_line = f"👤 *{user.full_name}*"
    message_text = (
        f"📩 Нове звернення\n"
        f"{name_line}\n"
        f"🆔 `{chat_id}`\n\n"
        f"💬 {text}"
    )

    keyboard = [[
        InlineKeyboardButton("❌ Закрити", callback_data=f"close_support|{chat_id}"),
        InlineKeyboardButton("✏️ Відповісти", callback_data=f"reply_to_user|{chat_id}")
    ]]
    markup = InlineKeyboardMarkup(keyboard)

    for admin_id in admin_ids:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=message_text,
                parse_mode="Markdown",
                reply_markup=markup
            )
        except Exception as e:
            print(f"Помилка при відправці адміну {admin_id}: {e}")

    await update.message.reply_text("✅ Ваше звернення передано підтримці! Ми відповімо якнайшвидше.")


async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❗ Формат: /reply <chat_id> <текст>")
        return

    chat_id = context.args[0]
    text = " ".join(context.args[1:])

    try:
        user_info = await context.bot.get_chat(chat_id)
        name = user_info.full_name
    except Exception:
        name = "невідомо"

    try:
        await context.bot.send_message(chat_id=chat_id, text=text)
        await update.message.reply_text(
            f"✅ Повідомлення надіслано користувачу *{name}* (ID: `{chat_id}`)",
            parse_mode="Markdown"
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Помилка при надсиланні: {e}"
        )
