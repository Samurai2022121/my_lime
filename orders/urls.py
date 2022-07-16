from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from .views import OrderLineOfferViewset, OrderLineViewset, OrderViewset

router = SimpleRouter()
router.register("orders", OrderViewset)
line_router = NestedSimpleRouter(router, "orders", lookup="order")
line_router.register("lines", OrderLineViewset, basename="orderline")
offer_router = NestedSimpleRouter(line_router, "lines", lookup="line")
offer_router.register("offers", OrderLineOfferViewset, basename="orderlineoffer")

urlpatterns = [
    path(
        r"outlets/<int:shop_id>/",
        include(router.urls + line_router.urls + offer_router.urls),
    ),
]
