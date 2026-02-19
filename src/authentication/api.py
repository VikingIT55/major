from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from authentication.serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny, )
    serializer_class = CustomTokenObtainPairSerializer
