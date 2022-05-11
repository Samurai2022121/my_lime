from django.db.models import F, Sum
from django_filters import rest_framework as df_filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from utils.views_utils import (
    BulkChangeArchiveStatusViewSetMixin,
    BulkUpdateViewSetMixin,
    ChangeDestroyToArchiveMixin,
    OrderingModelViewsetMixin,
)

from .. import filters, models, serializers


class WarehouseOrderViewSet(
    ChangeDestroyToArchiveMixin,
    ModelViewSet,
    OrderingModelViewsetMixin,
):
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.WarehouseOrderFilter
    permission_classes = (AllowAny,)
    serializer_class = serializers.WarehouseOrderSerializer
    lookup_field = "id"
    queryset = models.WarehouseOrder.objects

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .prefetch_related(
                "warehouse_order_positions",
                "supplier__supply_contract",
                "supplier",
                "shop",
                "receipts",
            )
            .annotate(
                total=Sum(
                    F("warehouse_order_positions__quantity")
                    * F("warehouse_order_positions__buying_price")
                )
            )
            .order_by("created_at")
        )

        if "is_archive" not in self.request.query_params:
            qs = qs.filter(is_archive=False)

        ordering_fields = self.get_ordering_fields()
        if ordering_fields:
            return qs.order_by(*ordering_fields)
        return qs


class SupplierViewSet(
    ChangeDestroyToArchiveMixin,
    BulkChangeArchiveStatusViewSetMixin,
    BulkUpdateViewSetMixin,
    ModelViewSet,
    OrderingModelViewsetMixin,
):
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.SupplierFilter
    permission_classes = (AllowAny,)
    serializer_class = serializers.SupplierSerializer
    lookup_field = "id"
    queryset = models.Supplier.objects.all()

    def get_queryset(self):
        qs = self.queryset
        if "is_archive" not in self.request.query_params:
            qs = qs.filter(is_archive=False)
        ordering_fields = self.get_ordering_fields()
        if ordering_fields:
            return qs.order_by(*ordering_fields)
        return qs.order_by("name")


class SupplyContractViewSet(BulkChangeArchiveStatusViewSetMixin, ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.SupplyContractsSerializer
    lookup_field = "id"
    queryset = models.SupplyContract.objects.all()
    serializer_action_classes = {
        "create": serializers.SupplyContractsSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action, super().get_serializer_class()
        )

    def post(self, request, format=None):
        data = request.data
        serializer = self.get_serializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class LegalEntityViewSet(ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.LegalEntitySerializer
    lookup_field = "registration_id"
    queryset = models.LegalEntities.objects.filter(active="+")
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.LegalEntityFilterSet

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paginator.page_size = 30
