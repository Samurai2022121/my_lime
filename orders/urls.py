from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from .views import (
    AlfaCallBackView,
    OrderLineOfferViewset,
    OrderLineViewset,
    OrderPayView,
    OrderViewset,
)

router = SimpleRouter()
router.register("orders", OrderViewset)
line_router = NestedSimpleRouter(router, "orders", lookup="order")
line_router.register("lines", OrderLineViewset, basename="orderline")
offer_router = NestedSimpleRouter(line_router, "lines", lookup="line")
offer_router.register("offers", OrderLineOfferViewset, basename="orderlineoffer")
order_pay_router = SimpleRouter()
order_pay_router.register("order-pay", OrderPayView)


urlpatterns = [
    path("", include(order_pay_router.urls)),
    path(
        r"outlets/<int:shop_id>/",
        include(router.urls + line_router.urls + offer_router.urls),
    ),
    path("alfa-callback/<int:id>", AlfaCallBackView.as_view(), name="alfa-callback"),
]
