from django_filters import rest_framework as df_filters
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin

from utils.serializers_utils import exclude_field
from utils.views_utils import (
    BulkChangeArchiveStatusViewSetMixin,
    BulkUpdateViewSetMixin,
    ChangeDestroyToArchiveMixin,
    OrderingModelViewsetMixin,
)

from .. import filters, models, serializers


class ShopViewSet(
    ChangeDestroyToArchiveMixin,
    BulkChangeArchiveStatusViewSetMixin,
    BulkUpdateViewSetMixin,
    ModelViewSet,
    OrderingModelViewsetMixin,
):
    permission_classes = (AllowAny,)
    serializer_class = serializers.ShopSerializer
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.ShopFilter
    lookup_field = "id"
    queryset = models.Shop.objects.all()

    def get_queryset(self):
        qs = self.queryset
        if "is_archive" not in self.request.query_params:
            qs = qs.filter(is_archive=False)
        ordering_fields = self.get_ordering_fields()
        if ordering_fields:
            return qs.order_by(*ordering_fields)
        return qs.order_by("name")


class WarehouseViewSet(NestedViewSetMixin, ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.WarehouseSerializer
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.WarehouseFilter
    lookup_field = "id"
    parent_lookup_kwargs = {"shop_id": "shop__id"}
    queryset = models.Warehouse.objects

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paginator.page_size = None

    def get_queryset(self):
        qs = super().get_queryset().order_by("product_unit__product__name")
        return qs

    def get_serializer_class(self):
        serializer_class = super().get_serializer_class()
        if self.request.method == "get":
            serializer_class = exclude_field(serializer_class, "shop")
        return serializer_class

    def perform_create(self, serializer):
        serializer.save(shop_id=self.kwargs.get("shop_id", None))


class WarehouseRecordViewSet(NestedViewSetMixin, ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.WarehouseRecordSerializer
    lookup_field = "id"
    parent_lookup_kwargs = {
        "shop_id": "warehouse__shop_id",
        "warehouse_id": "warehouse__id",
    }
    queryset = models.WarehouseRecord.objects

    def get_serializer_class(self):
        serializer_class = super().get_serializer_class()
        if self.request.method == "get":
            serializer_class = exclude_field(serializer_class, "warehouse")
        return serializer_class

    def perform_create(self, serializer):
        serializer.save(
            warehouse_id=self.kwargs.get("warehouse_id", None),
        )


class BatchViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    lookup_field = "id"
    serializer_class = serializers.BatchSerializer
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.BatchFilter
    queryset = models.Batch.objects.order_by("created_at")
