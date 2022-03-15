from django.urls import include, path
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from news.views import NewsAdminViewset
from products.views import EditProductImagesViewset, ProductAdminViewset
from recipes.views import RecipeAdminViewset

from . import views

router = routers.SimpleRouter()
router.register("outlets", views.ShopViewSet)
router.register("personnel", views.PersonnelViewSet)
router.register("personnel-document", views.PersonnelDocumentViewSet)
router.register("product-orders", views.WarehouseOrderViewSet)
router.register("supplier", views.SupplierViewSet)
router.register("supply-contracts", views.SupplyContractViewSet)
router.register("legal-entities", views.LegalEntityViewSet)

warehouse_router = NestedSimpleRouter(router, "outlets", lookup="shop")
warehouse_router.register("warehouses", views.WarehouseViewSet)

warehouse_record_router = NestedSimpleRouter(
    warehouse_router,
    "warehouses",
    lookup="warehouse",
)
warehouse_record_router.register("records", views.WarehouseRecordViewSet)

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
]

urlpatterns += router.urls
urlpatterns += warehouse_router.urls
urlpatterns += warehouse_record_router.urls
