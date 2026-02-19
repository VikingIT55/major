from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from users.constants import Role
from users.serializers import UserSerializer, UserRegistrationSerializer


User = get_user_model()


class UserModelViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (
        IsAdminUser,
        IsAuthenticated,
    )
    queryset = User.objects.all()

    def get_queryset(self):
        user = self.request.user

        match True:
            case user.is_anonymous:
                return User.objects.none()

            case user.is_superuser | user.is_staff:
                return User.objects.all()

            case user.role:
                match user.role:
                    case Role.ADMIN | Role.MANAGER:
                        return User.objects.all()

                    case Role.USER:
                        return User.objects.filter(id=user.id)

            case user.is_authenticated:
                return User.objects.filter(id=user.id)

            case _:
                return User.objects.none()


class UserRegistrationCreateAPIView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (IsAdminUser,)
