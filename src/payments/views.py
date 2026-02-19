import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


from payments.serializers import (
    CreateInvoiceInSerializer,
    CreateInvoiceOutSerializer,
    InvoiceStatusSerializer,
)
from payments.utils import (
    cache_store_invoice,
    cache_pop_invoice,
    format_order_message,
    generate_reference_code,
    release_reference_code,
)
from payments.api import MonoClient
from payments.telegram_utils import send_order_to_admin


#Delete before deploy
def get_shop_admin_ids() -> list[int]:
    admin_ids = os.getenv("SHOP_ADMIN_ID", "")
    if not admin_ids:
        return []
    return [int(admin_id.strip()) for admin_id in admin_ids.split(",") if admin_id.strip()]

class CreateInvoiceView(APIView):
    @transaction.atomic
    def post(self, request):
        data_serializer = CreateInvoiceInSerializer(data=request.data)
        data_serializer.is_valid(raise_exception=True)
        valid_data = data_serializer.validated_data

        reference = generate_reference_code()

        payload = {
            "amount": valid_data["amount"],        
            "ccy": 980,              # 980 = UAH
            "merchantPaymInfo": {
                "destination": f"Оплата замовлення №{reference}",
                "comment": valid_data.get("phone") or "",
            },
            "webHookUrl": settings.MONOBANK.get("DEFAULT_WEBHOOK_URL") or None,
            "redirectUrl": settings.MONOBANK.get("DEFAULT_REDIRECT_URL") or None,
            "paymentType": "debit",
            "reference": reference,

        }

        client = MonoClient()
        out = client.create_invoice(payload)

        if out["status_code"] not in (200, 201):
            return Response(
                {"detail": "Monobank error", "monobank": out["json"]},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        resp_data = {
            "invoice_id": out["json"].get("invoiceId"),
            "page_url": out["json"].get("pageUrl"),
            "reference": reference,
        }

        cache_store_invoice(resp_data["invoice_id"], {
            "name": valid_data.get("name"),
            "last_name": valid_data.get("last_name"),
            "phone": valid_data.get("phone"),
            "telegram_name": valid_data.get("telegram_name"),
            "delivery_method": valid_data.get("delivery_method"),
            "settlement": valid_data.get("settlement"),
            "warehouse": valid_data.get("warehouse"),
            "comment": valid_data.get("comment"),
            "amount": valid_data.get("amount"),
            "full_amount": valid_data.get("full_amount"),
            "reference": reference,
            "ccy": valid_data.get("ccy", 980),
            "payment_option": valid_data.get("payment_option"),
            "products": valid_data.get("products"),
            "promocode": valid_data.get("promocode"),
        })

        return Response(CreateInvoiceOutSerializer(resp_data).data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class MonoWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        x_sign = request.headers.get("X-Sign", "")
        if not MonoClient.verify_webhook_signature(request.body, x_sign):
            return Response({"detail": "Invalid signature"}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        status_value = str(data.get("status", "")).lower()
        invoice_id = data.get("invoiceId")

        if status_value in ("success", "paid"):
            full = cache_pop_invoice(invoice_id) or {
                "name": "-",
                "last_name": "-",
                "phone": "-",
                "telegram_name": None,
                "delivery_method": "pickup",
                "settlement": None,
                "warehouse": None,
                "comment": None,
                "amount": data.get("amount"),
                "full_amount": data.get("amount"),
                "reference": data.get("reference"),
                "destination": data.get("destination"),
                "ccy": data.get("ccy", 980),
                "payment_option": "full",
                "products": data.get("products", []),
                "promocode": None,
            }

            message = format_order_message(full)
            admin_ids = get_shop_admin_ids()

            for admin_id in admin_ids:
                try:
                    send_order_to_admin(
                        admin_id,
                        message,
                        full.get("name") or "-",
                        full.get("last_name") or "-",
                        full.get("reference") or "-",
                    )
                except Exception as e:
                    print(f"Telegram send error: {e}")

        elif status_value in ("failure", "expired", "reversed", "refund", "refunded", "canceled"):
            full = cache_pop_invoice(invoice_id)
            if full:
                reference = full.get("reference")
                release_reference_code(reference)

        return Response({"ok": True}, status=status.HTTP_200_OK)
    
class InvoiceStatusView(APIView):
    def get(self, request, invoice_id: str):
        client = MonoClient()
        out = client.get_invoice_status(invoice_id)

        if out["status_code"] == 404:
            return Response(
                {"detail": "Invoice not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        elif out["status_code"] != 200:
            return Response(
                {"detail": "Monobank error", "monobank": out["json"]},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        resp_data = {
            "invoice_id": invoice_id,
            "status": out["json"].get("status", "unknown"),
            "amount": out["json"].get("amount"),
            "ccy": out["json"].get("ccy"),
        }
        return Response(InvoiceStatusSerializer(resp_data).data, status=status.HTTP_200_OK)
