from django.urls import path

from delivery.views import (NovaPoshtaSettlementSearchView,
                            NovaPoshtaWarehousesView)


urlpatterns = [
    path("search-settlements/", NovaPoshtaSettlementSearchView.as_view(), name="search-settlements"),
    path("warehouses/", NovaPoshtaWarehousesView.as_view(), name="search-warehouses"),
]
