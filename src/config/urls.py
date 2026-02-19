from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny
from django.contrib.sitemaps.views import sitemap

from django.conf import settings
from django.conf.urls.static import static
from products.sitemaps import ProductSitemap


ROOT_API = "api/v1"
sitemaps_dict = {"products": ProductSitemap}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        f"{ROOT_API}/auth/",
        include(("authentication.urls", "authentication"), namespace="authentication"),
    ),
    path(
        f"{ROOT_API}/users/",
        include(("users.urls", "users"), namespace="users"),
    ),
    path(
        f"{ROOT_API}/products/",
        include(("products.urls", "products"), namespace="products"),
    ),
    path(
        f"{ROOT_API}/delivery/",
        include(("delivery.urls", "delivery"), namespace="delivery")
    ),
    path(
        f"{ROOT_API}/blog/",
        include(("blog.urls", "blog"), namespace="blog"),
    ),
    path(
        f"{ROOT_API}/partners/",
        include(("partners.urls", "partners"), namespace="partners"),
    ),
    path(
        f"{ROOT_API}/contacts/",
        include(("contacts.urls", "contacts"), namespace="contacts"),
    ),
    path(
        f"{ROOT_API}/payments/",
        include(("payments.urls", "payments"), namespace="payments"),
    ),
    path(
        f"{ROOT_API}/telegram-bot/",
        include(("telegram_bot.urls", "telegram_bot"), namespace="telegram_bot"),
    ),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps_dict}, name="sitemap"),


]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
