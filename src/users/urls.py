from django.urls import path
from rest_framework.routers import DefaultRouter

from users.api import UserModelViewSet, UserRegistrationCreateAPIView


router = DefaultRouter()
router.register("", UserModelViewSet)

urlpatterns = [
    path("registration/", UserRegistrationCreateAPIView.as_view()),
] + router.urls
