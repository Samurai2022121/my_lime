from .autocomplete import Autocomplete
from .internet_equaring import OrderPayView
from .primary_documents import (  # noqa
    CancelDocumentViewSet,
    ConversionDocumentViewSet,
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
    AlfaCallBackView,
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
