from django.urls import include, path
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
router.register("legal-entities", views.LegalEntityViewSet)

router.register("product", ProductAdminViewset)
router.register("product-images", EditProductImagesViewset)
router.register("news", NewsAdminViewset)
router.register("recipes", RecipeAdminViewset)

docs_router = routers.SimpleRouter()
docs_router.register("production", views.ProductionDocumentViewSet)
docs_router.register("inventory", views.InventoryDocumentViewSet)
docs_router.register("write-offs", views.WriteOffDocumentViewSet)
docs_router.register("conversion", views.ConversionDocumentViewSet)
docs_router.register("move", views.MoveDocumentViewSet)
docs_router.register("receipts", views.ReceiptDocumentViewSet)
docs_router.register("sales", views.SaleDocumentViewSet)
docs_router.register("cancel", views.CancelDocumentViewSet)

urlpatterns = [
    path("primary-documents/", include(docs_router.urls)),
    path("upload-csv/", views.UploadCSVGenericView.as_view(), name="csv-upload"),
    path("matrix-products/", ProductMatrixViewset.as_view(), name="matrix-products"),
]

urlpatterns += router.urls
