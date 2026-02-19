from django.contrib.auth import get_user_model
from rest_framework.serializers import CharField, Serializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["salt"] = "MAJOR"
        token["role"] = user.role

        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # add role to response
        data['role'] = self.user.role

        return data


class LoginResponseSerializer(Serializer):
    refresh = CharField()
    access = CharField()
    role = CharField() 


class RefreshTokenResponseSerializer(Serializer):
    access = CharField()
