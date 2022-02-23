from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from .views import (
    CategoryViewset,
    ConversionSourceViewset,
    ConversionTargetViewset,
    MeasurementUnitViewset,
    ProductAdminViewset,
    ProductUnitViewset,
    ProductViewset,
)

router = routers.SimpleRouter()
router.register("units", MeasurementUnitViewset)
router.register("products", ProductViewset)
router.register("categories", CategoryViewset)
router.register("admin-products", ProductAdminViewset)

product_unit_router = NestedSimpleRouter(router, "products", lookup="product")
product_unit_router.register("units", ProductUnitViewset)

conversion_router = NestedSimpleRouter(
    product_unit_router,
    "units",
    lookup="unit",
)
conversion_router.register("sources", ConversionSourceViewset, basename="sources")
conversion_router.register("targets", ConversionTargetViewset, basename="targets")

urlpatterns = router.urls
urlpatterns += product_unit_router.urls
urlpatterns += conversion_router.urls
