from django.urls import include, path
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from news.views import NewsAdminViewset
from products.views import EditProductImagesViewset, ProductAdminViewset
from recipes.views import RecipeAdminViewset

from . import views

router = routers.SimpleRouter()
router.register("outlets", views.ShopViewSet)
router.register("product-orders", views.WarehouseOrderViewSet)
router.register("supplier", views.SupplierViewSet)
router.register("supply-contracts", views.SupplyContractViewSet)
router.register("legal-entities", views.LegalEntityViewSet)
router.register("batches", views.BatchViewSet)

warehouse_router = NestedSimpleRouter(router, "outlets", lookup="shop")
warehouse_router.register("warehouses", views.WarehouseViewSet)
warehouse_router.register(
    "warehouses-scales",
    views.WarehouseForScalesListView,
    basename="warehouseforscales",
)

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
production_records_router = NestedSimpleRouter(
    docs_router, "production", lookup="document"
)
production_records_router.register(
    "records", views.PrimaryDocumentRecordViewSet, basename="productionrecord"
)

docs_router.register("inventory", views.InventoryDocumentViewSet)
inventory_records_router = NestedSimpleRouter(
    docs_router, "inventory", lookup="document"
)
inventory_records_router.register(
    "records", views.PrimaryDocumentRecordViewSet, basename="inventoryrecord"
)

docs_router.register("write-offs", views.WriteOffDocumentViewSet)
write_offs_records_router = NestedSimpleRouter(
    docs_router, "write-offs", lookup="document"
)
write_offs_records_router.register(
    "records", views.PrimaryDocumentRecordViewSet, basename="writeoffrecord"
)

docs_router.register("conversion", views.ConversionDocumentViewSet)
conversion_records_router = NestedSimpleRouter(
    docs_router, "conversion", lookup="document"
)
conversion_records_router.register(
    "records", views.PrimaryDocumentRecordViewSet, basename="conversionrecord"
)

docs_router.register("move", views.MoveDocumentViewSet)
move_records_router = NestedSimpleRouter(docs_router, "move", lookup="document")
move_records_router.register(
    "records", views.PrimaryDocumentRecordViewSet, basename="moverecord"
)

docs_router.register("receipts", views.ReceiptDocumentViewSet)
receipts_records_router = NestedSimpleRouter(docs_router, "receipts", lookup="document")
receipts_records_router.register(
    "records", views.PrimaryDocumentRecordViewSet, basename="receiptrecord"
)

docs_router.register("sales", views.SaleDocumentViewSet)
sales_records_router = NestedSimpleRouter(docs_router, "sales", lookup="document")
sales_records_router.register(
    "records", views.PrimaryDocumentRecordViewSet, basename="salerecord"
)

docs_router.register("cancel", views.CancelDocumentViewSet)
cancel_records_router = NestedSimpleRouter(docs_router, "cancel", lookup="document")
cancel_records_router.register(
    "records", views.PrimaryDocumentRecordViewSet, basename="cancelrecord"
)

docs_router.register("return", views.ReturnDocumentViewSet)
return_records_router = NestedSimpleRouter(docs_router, "return", lookup="document")
return_records_router.register(
    "records", views.PrimaryDocumentRecordViewSet, basename="returnrecord"
)
docs_router.register("graph-analytics", views.GraphAnalyticsViewSet)

urlpatterns = [
    path("primary-documents/", include(docs_router.urls)),
    path("primary-documents/", include(production_records_router.urls)),
    path("primary-documents/", include(inventory_records_router.urls)),
    path("primary-documents/", include(write_offs_records_router.urls)),
    path("primary-documents/", include(conversion_records_router.urls)),
    path("primary-documents/", include(move_records_router.urls)),
    path("primary-documents/", include(receipts_records_router.urls)),
    path("primary-documents/", include(sales_records_router.urls)),
    path("primary-documents/", include(cancel_records_router.urls)),
    path("primary-documents/", include(return_records_router.urls)),
    path("upload-csv/", views.UploadCSVGenericView.as_view(), name="csv-upload"),
    path("autocomplete/", views.Autocomplete.as_view(), name="autocomplete"),
]

urlpatterns += router.urls
urlpatterns += warehouse_router.urls
urlpatterns += warehouse_record_router.urls
