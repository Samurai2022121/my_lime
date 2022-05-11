from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from .views import (
    BuyerCountViewSet,
    LoyaltyCardViewSet,
    OfferViewSet,
    RangeViewSet,
    VoucherViewSet,
)

router = routers.SimpleRouter()
router.register("offers", OfferViewSet)
router.register("ranges", RangeViewSet)
router.register("vouchers", VoucherViewSet)
router.register("loyalty-cards", LoyaltyCardViewSet)

buyer_count_router = NestedSimpleRouter(router, "offers", lookup="offer")
buyer_count_router.register("buyer-counts", BuyerCountViewSet)

urlpatterns = router.urls + buyer_count_router.urls
