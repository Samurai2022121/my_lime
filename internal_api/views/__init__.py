from .autocomplete import Autocomplete
from .primary_documents import (  # noqa
    CancelDocumentViewSet,
    ConversionDocumentViewSet,
    GraphAnalyticsViewSet,
    GraphCheckAnalyticsViewSet,
    InventoryDocumentViewSet,
    MoveDocumentViewSet,
    PrimaryDocumentRecordViewSet,
    ProductionDocumentViewSet,
    ReceiptDocumentViewSet,
    ReturnDocumentViewSet,
    SaleDocumentViewSet,
    WriteOffDocumentViewSet,
)
from .shops import (  # noqa
    BatchViewSet,
    ShopViewSet,
    WarehouseForScalesListView,
    WarehouseRecordViewSet,
    WarehouseViewSet,
)
from .suppliers import (  # noqa
    LegalEntityViewSet,
    SupplierViewSet,
    SupplyContractViewSet,
    WarehouseOrderViewSet,
)
from .upload_csv import UploadCSVGenericView  # noqa
