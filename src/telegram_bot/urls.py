from django.urls import path
from telegram_bot.views import CustomerHelpRequestView, CooperationRequestView

urlpatterns = [
    path("support/", CustomerHelpRequestView.as_view(), name="support"),
    path("cooperation/", CooperationRequestView.as_view(), name="cooperation"),
]
