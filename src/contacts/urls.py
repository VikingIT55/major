from rest_framework import routers

from contacts.api import ContactViewSet

router = routers.DefaultRouter()
router.register(r"", ContactViewSet, basename="contacts")

urlpatterns = [
    
] + router.urls