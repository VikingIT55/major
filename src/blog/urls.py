from rest_framework.routers import DefaultRouter

from blog.api import BlogViewSet, BlogImageViewSet


router = DefaultRouter()
router.register("posts", BlogViewSet, basename="posts")
router.register("images", BlogImageViewSet, basename="images")
urlpatterns = [
    
] + router.urls
