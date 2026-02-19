from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django_filters import CharFilter, ModelMultipleChoiceFilter
from django_filters.rest_framework import (BooleanFilter, DjangoFilterBackend,
                                           FilterSet, NumberFilter)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from products.models import (BannerProduct, Product, ProductPurposeCategory,
                             ProductReview, ProductTypeCategory, PromoCode)
from products.permissions import (ReviewPermission, RoleIsAdmin, RoleIsManager,
                                  RoleIsUser)
from products.serializers import (BannerProductSerializer,
                                  ProductPurposeCategorySerializer,
                                  ProductReviewSerializer, ProductSerializer,
                                  ProductTypeCategorySerializer,
                                  PromoCodeSerializer,
                                  PromoCodeValidateResponseSerializer,
                                  PromoCodeValidateSerializer)


class CaseInsensitiveSearchFilter(SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_query = self.get_search_terms(request)
        if not search_query:
            return queryset
        search_query_lower = [term.lower() for term in search_query]
        name_uk_values = list(
            queryset.values_list("product_name_uk", flat=True)
            )
        name_en_values = list(
            queryset.values_list("product_name_en", flat=True)
            )
        matching_uk = [
            name
            for name in name_uk_values
            if any(term in name.lower() for term in search_query_lower)
        ]
        matching_en = [
            name
            for name in name_en_values
            if any(term in name.lower() for term in search_query_lower)
        ]
        q_objects = Q(product_name_uk__in=matching_uk) | Q(
            product_name_en__in=matching_en
        )
        filtered_queryset = queryset.filter(q_objects)

        if not filtered_queryset.exists():
            raise ValidationError(
                {"error": "No products found for the given search term."}
            )

        return filtered_queryset


class ProductFilter(FilterSet):
    id = CharFilter(
        method="filter_by_ids", label="Comma-separated product IDs"
        )
    is_discount = BooleanFilter(
        method="is_discount_filter", label="Is Discount"
        )
    min_price = NumberFilter(
        field_name="price_with_discount", lookup_expr="gte", label="Min Price"
        )
    max_price = NumberFilter(
        field_name="price_with_discount", lookup_expr="lte", label="Max Price"
        )
    type = ModelMultipleChoiceFilter(
        queryset=ProductTypeCategory.objects.annotate(
            product_count=Count("products")
            ),
        field_name="type_category",
        to_field_name="id",
        label="Type Category",
    )

    def is_discount_filter(self, queryset, name, value):
        return queryset.filter(
            discount__gt=0) if value else queryset.filter(discount=0
                                                          )

    def filter_by_ids(self, queryset, name, value):
        try:
            ids = [int(i.strip()) for i in value.split(",") if i.isdigit()]
            return queryset.filter(id__in=ids)
        except Exception:
            return queryset.none()

    class Meta:
        model = Product
        fields = ["is_new", "is_best_seller", "purpose_category", "type"]



class PromoCodeFilter(FilterSet):
    is_active = BooleanFilter(method='filter_is_active')

    class Meta:
        model = PromoCode
        fields = []

    def filter_is_active(self, queryset, name, value):
        time_now = now()
        if value:
            return queryset.filter(started_at__lte=time_now, expires_at__gte=time_now)
        else:
            return queryset.exclude(started_at__lte=time_now, expires_at__gte=time_now)


class ProductPurposeCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductPurposeCategory.objects.all()
    serializer_class = ProductPurposeCategorySerializer
    permission_classes = [RoleIsAdmin | RoleIsManager | RoleIsUser]


class ProductTypeCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductTypeCategory.objects.annotate(
        product_count=Count("products")
        )
    serializer_class = ProductTypeCategorySerializer
    permission_classes = [RoleIsAdmin | RoleIsManager | RoleIsUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.product_count > 0:
            return Response(
                {
                    "error": _(
                        "Cannot delete category because it is associated with products. "
                        "Products count: {}"
                    ).format(instance.product_count)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("price_with_discount")
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, CaseInsensitiveSearchFilter]
    filterset_class = ProductFilter
    search_fields = ["product_name_uk", "product_name_en"]
    permission_classes = [RoleIsAdmin | RoleIsManager | RoleIsUser]


class ProductReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ProductReviewSerializer
    permission_classes = [ReviewPermission]

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        if product_id:
            return ProductReview.objects.filter(product_id=product_id)
        return ProductReview.objects.none()

    def create(self, request, *args, **kwargs):
        product_id = kwargs.get("product_id") or request.data.get("product_id")
        if not product_id:
            return Response({"error": _("Product ID is required")}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = get_object_or_404(Product, id=product_id)
        serializer.save(product=product, is_approved=False)
        return Response(serializer.data, status=201)

    @action(
            detail=True,
            methods=["post"],
            permission_classes=[RoleIsAdmin | RoleIsManager]
            )
    def approve(self, request, *args, **kwargs):
        product_id = self.kwargs.get("product_id")
        pk = self.kwargs.get("pk")

        if not str(pk).isdigit():
            return Response(
                {"error": "Invalid review ID."},
                status=status.HTTP_404_NOT_FOUND
                )
        review = get_object_or_404(ProductReview, pk=pk, product_id=product_id)
        review.is_approved = True
        review.save()
        return Response({"status": "approved"}, status=status.HTTP_200_OK)

    @action(
            detail=True,
            methods=["post"],
            permission_classes=[RoleIsAdmin | RoleIsManager]
            )
    def reject(self, request, *args, **kwargs):
        product_id = self.kwargs.get("product_id")
        pk = self.kwargs.get("pk")

        if not str(pk).isdigit():
            return Response(
                {"error": "Invalid review ID."},
                status=status.HTTP_404_NOT_FOUND
                )
        review = get_object_or_404(ProductReview, pk=pk, product_id=product_id)
        review.is_approved = False
        review.save()
        return Response({"status": "rejected"}, status=status.HTTP_200_OK)


class PromoCodeViewSet(viewsets.ModelViewSet):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PromoCodeFilter
    permission_classes = [RoleIsAdmin | RoleIsManager]
    
    @action(
            detail=False,
            methods=["post"],
            url_path="validate",
            permission_classes=[],
            serializer_class=PromoCodeValidateSerializer
            )
    def validate_promocode(self, request):
        input_serializer = PromoCodeValidateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        code = input_serializer.validated_data["code"]
        try:
            promo = PromoCode.objects.get(code__iexact=code)
        except PromoCode.DoesNotExist:
            return Response(
                {"error": "Promo code not found"},
                status=status.HTTP_400_BAD_REQUEST
                )

        if not promo.is_active:
            return Response(
                {"error": "Sorry, the promo code is not active."},
                status=status.HTTP_400_BAD_REQUEST
                )

        response_serializer = PromoCodeValidateResponseSerializer(
            {"discount_percent": promo.discount_percent}
            )
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    def filter_queryset(self, queryset):
        is_active_param = self.request.query_params.get('is_active')
        
        if is_active_param and is_active_param.lower() not in ['true', 'false']:
            raise ValidationError(
                {"is_active": "Must be either 'true' or 'false'."}
            )
        
        return super().filter_queryset(queryset)


class BannerProductViewSet(viewsets.ModelViewSet):
    queryset = BannerProduct.objects.all()
    serializer_class = BannerProductSerializer
    permission_classes = [RoleIsAdmin | RoleIsManager | RoleIsUser]


class AllProductReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_approved"]
    permission_classes = [RoleIsAdmin | RoleIsManager | RoleIsUser]

    def get_queryset(self):
        is_approved = self.request.query_params.get("is_approved")
        if is_approved is not None:
            value = str(is_approved).strip().lower()
            if value not in ["true", "false"]:
                raise ValidationError(
                    {"is_approved": "Must be either 'true' or 'false'."}
                    )
            bool_value = value == "true"
            return ProductReview.objects.filter(is_approved=bool_value)
        return ProductReview.objects.all()
