from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register("outlets", views.ShopViewSet)
router.register("personnel", views.PersonnelViewSet)
router.register("matrix", views.WarehouseViewSet)
router.register("product-orders", views.WarehouseOrderViewSet)
router.register("supplier", views.SupplierViewSet)
router.register("supply-contracts", views.SupplyContractViewSet)
router.register("tech-card", views.TechCardViewSet)
router.register("daily-menu", views.DailyMenuViewSet)
router.register("legal-entities", views.LegalEntityViewSet)


urlpatterns = [
    path("upload-csv/", views.UploadCSVGenericView.as_view(), name="csv-upload"),
]

urlpatterns += router.urls
