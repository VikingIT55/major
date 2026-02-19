import secrets
from datetime import datetime
from django.core.cache import cache

CACHE_TTL = 60 * 60 * 24  # 24h

def cache_store_invoice(invoice_id: str, data: dict, ttl: int = CACHE_TTL):
    cache.set(f"invoice:{invoice_id}", data, ttl)

def cache_pop_invoice(invoice_id: str):
    key = f"invoice:{invoice_id}"
    data = cache.get(key)
    if data is not None:
        cache.delete(key)
    return data

def format_order_message(data: dict) -> str:
    lines = []
    lines.append("✅ Оплата успішна!")
    lines.append(f"🧾 Замовлення: *{data.get('reference','-')}*")
    amount = (data.get("amount")) / 100
    full_amount = (data.get("full_amount")) / 100
    lines.append(f"💰 Оплачено: {amount:.2f} грн")
    lines.append(f"💰 Повна сума: {full_amount:.2f} грн")
    if data.get("promocode"):
        lines.append(f"🎫 Промокод: {data.get('promocode','-')}")
    lines.append("")
    lines.append("👤 Покупець:")
    lines.append(f"• Імʼя: {data.get('name','-')}")
    lines.append(f"• Прізвище: {data.get('last_name','-')}")
    lines.append(f"• Телефон: {data.get('phone','-')}")
    lines.append(f"• Оплата: {data.get('payment_option','full').capitalize()}")
    if data.get("telegram_name"):
        lines.append(f"• Telegram: {data['telegram_name']}")
    lines.append("")
    lines.append("🛒 Товари:"),
    for product in data.get("products", []):
        name = product.get("name", "-")
        article = product.get("article", "")
        number_of_items = product.get("number_of_items", 1)
        price_with_discount = (product.get("price_with_discount", 0)) / 100
        lines.append(f"• {name} {article} - {number_of_items} шт. по {price_with_discount:.2f} грн")
    lines.append("")
    delivery_method = data.get("delivery_method", "pickup")
    if delivery_method == "pickup":
        lines.append("🚚 Доставка: самовивіз")
    elif delivery_method == "nova_poshta":
        lines.append(f"🚚 Нова Пошта: {data.get('settlement','-')}, відділення {data.get('warehouse','-')}")
    if data.get("comment"):
        lines.append("")
        lines.append(f"📝 Коментар: {data['comment']}")
    return "\n".join(lines)

def generate_reference_code(ttl_seconds: int = CACHE_TTL * 30) -> str:
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    month_letters = 'JFMAMJJASOND'
    month_index = datetime.now().month
    month_prefix = month_letters[month_index - 1]

    while True:
        random_part = ''.join(secrets.choice(alphabet) for _ in range(3))
        reference_code = f"{month_prefix}{random_part}"
        if not cache.get(f"reference_code:{reference_code}"):
            cache.set(f"reference_code:{reference_code}", True, ttl_seconds)
            return reference_code
        
def release_reference_code(reference_code: str):
    if not reference_code:
        return
    cache.delete(f"reference_code:{reference_code}")