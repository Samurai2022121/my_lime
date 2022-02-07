from django.urls import path
from rest_framework import routers

from news.views import NewsAdminViewset
from products.views import (
    EditProductImagesViewset,
    ProductAdminViewset,
    ProductMatrixViewset,
)
from recipes.views import RecipeAdminViewset

from . import views

router = routers.SimpleRouter()
router.register("outlets", views.ShopViewSet)
router.register("personnel", views.PersonnelViewSet)
router.register("personnel-document", views.PersonnelDocumentViewSet)
router.register("matrix", views.WarehouseViewSet)
router.register("product-orders", views.WarehouseOrderViewSet)
router.register("supplier", views.SupplierViewSet)
router.register("supply-contracts", views.SupplyContractViewSet)
router.register("tech-card", views.TechCardViewSet)
router.register("daily-menu", views.DailyMenuViewSet)
router.register("legal-entities", views.LegalEntityViewSet)

router.register("product", ProductAdminViewset)
router.register("product-images", EditProductImagesViewset)
router.register("news", NewsAdminViewset)
router.register("recipes", RecipeAdminViewset)

urlpatterns = [
    path("upload-csv/", views.UploadCSVGenericView.as_view(), name="csv-upload"),
    path("matrix-products/", ProductMatrixViewset.as_view(), name="matrix-products"),
]

urlpatterns += router.urls
