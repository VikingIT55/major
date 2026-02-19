from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from telegram_bot.serializers import CooperationSerializer, SupportSerializer
from telegram_bot.support_api import send_support_message


class CooperationRequestView(APIView):
    def post(self, request):
        ser = CooperationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        send_support_message(
            "🤝 *НОВИЙ ЗАПИТ НА СПІВПРАЦЮ*",
            data["name"],
            data["phone"],
            question=None
        )

        return Response({"ok": True}, status=status.HTTP_200_OK)
    
class CustomerHelpRequestView(APIView):
    def post(self, request):
        ser = SupportSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        send_support_message(
            "🆘 *КЛІЄНТ ПРОСИТЬ ЗВʼЯЗАТИСЯ*",
            data["name"],
            data["phone"],
            question=data["question"]
        )

        return Response({"ok": True}, status=status.HTTP_200_OK)
    