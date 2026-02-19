from rest_framework.routers import DefaultRouter

from products.api import (AllProductReviewViewSet, BannerProductViewSet,
                          ProductPurposeCategoryViewSet, ProductReviewViewSet,
                          ProductTypeCategoryViewSet, ProductViewSet,
                          PromoCodeViewSet)


router = DefaultRouter()
router.register("product_purpose_categories", ProductPurposeCategoryViewSet)
router.register("product_type_categories", ProductTypeCategoryViewSet)
router.register("products_list", ProductViewSet, basename="products")
router.register(
    r"reviews/(?P<product_id>\d+)", ProductReviewViewSet, basename="product-reviews"
)
router.register("promocodes", PromoCodeViewSet, basename="promocode")
router.register("banner_products", BannerProductViewSet, basename="banner-products")
router.register("reviews", AllProductReviewViewSet, basename="all-reviews")

urlpatterns = [
    
] + router.urls
