from rest_framework.routers import DefaultRouter

from partners.api import PartnerLocationViewSet


router = DefaultRouter()
router.register("location", PartnerLocationViewSet, basename="location")
urlpatterns = [
    
] + router.urls
