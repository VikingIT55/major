from django.urls import path
from payments.views import CreateInvoiceView, MonoWebhookView, InvoiceStatusView

urlpatterns = [
    path("create-invoice/", CreateInvoiceView.as_view(), name="mono-create-invoice"),
    path("webhook/monobank/", MonoWebhookView.as_view(), name="mono-webhook"),
    path("status/<str:invoice_id>/", InvoiceStatusView.as_view(), name="mono-invoice-status"),
]
