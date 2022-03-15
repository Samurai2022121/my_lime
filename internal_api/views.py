from decimal import Decimal

import pandas as pd
from django.db import transaction
from django.db.models import F, Sum
from django.utils.decorators import method_decorator
from django_filters import rest_framework as df_filters
from rest_framework.exceptions import APIException
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin

from products.models import Product
from products.serializers import ProductListSerializer
from utils.serializers_utils import exclude_field
from utils.views_utils import (
    BulkChangeArchiveStatusViewSetMixin,
    BulkUpdateViewSetMixin,
    ChangeDestroyToArchiveMixin,
    OrderingModelViewsetMixin,
)

from . import filters, models, serializers


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


class PersonnelViewSet(
    ChangeDestroyToArchiveMixin,
    BulkChangeArchiveStatusViewSetMixin,
    ModelViewSet,
    OrderingModelViewsetMixin,
):
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.PersonnelFilter
    permission_classes = (AllowAny,)
    serializer_class = serializers.PersonnelSerializer
    lookup_field = "id"
    queryset = models.Personnel.objects.all()

    def get_queryset(self):
        qs = self.queryset
        if "is_archive" not in self.request.query_params:
            qs = qs.filter(is_archive=False)
        return qs


class WarehouseViewSet(NestedViewSetMixin, ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.WarehouseSerializer
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.WarehouseFilter
    lookup_field = "id"
    parent_lookup_kwargs = {"shop_id": "shop__id"}
    queryset = models.Warehouse.objects

    def get_queryset(self):
        qs = super().get_queryset().order_by("product_unit__product__name")
        return qs

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
        return exclude_field(serializer, "shop")

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
        serializer = super().get_serializer_class()
        return exclude_field(serializer, "warehouse")

    def perform_create(self, serializer):
        serializer.save(
            warehouse_id=self.kwargs.get("warehouse_id", None),
        )


class UploadCSVGenericView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.UploadCSVSerializer
    queryset = Product.objects.all()

    product_fields_mapping = {
        "price_col": "price",
        "name_col": "name",
        "barcode_col": "barcode",
        "vat_col": "vat_value",
        "measure_unit_col": "measure_unit",
        "origin_col": "origin",
        "supplier_col": "manufacturer",
    }

    def post(self, request):
        context = {"request": request}

        serialized_data = self.serializer_class(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        data = serialized_data.validated_data

        file = pd.read_excel(data.get("csv_file", None), engine="openpyxl")

        file = file.where(pd.notnull(file), None)
        products = []
        row_num = data.get("first_row", None)

        for _, row in file.iloc[row_num:].iterrows():

            if row[data.get("name_col", 0)] and row[data.get("price_col", 0)]:

                name = row[data.get("name_col", None)]
                price = Decimal(row[data.get("price_col", None)])
                products.append(
                    Product(
                        name=name,
                        price=price,
                        barcode=row[data["barcode_col"]]
                        if data.get("barcode_col", None)
                        else None,
                        vat_value=str(row[data["vat_col"]]).replace("%", "")
                        if data.get("vat_col", None)
                        else None,
                        measure_unit=row[data["measure_unit_col"]]
                        # TODO: fix creation of measurement units
                        if data.get("measure_unit_col", None) else None,
                        origin=row[data["origin_col"]]
                        if data.get("origin_col", None)
                        else None,
                        manufacturer=row[data["supplier_col"]]
                        if data.get("supplier_col", None)
                        else None,
                    )
                )

        created_products = Product.objects.bulk_create(products, ignore_conflicts=True)
        serializer = ProductListSerializer(created_products, many=True, context=context)

        return Response(status=HTTP_202_ACCEPTED, data=serializer.data)


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
    queryset = models.WarehouseOrder.objects.all()

    def get_queryset(self):
        qs = self.queryset.prefetch_related("warehouse_order_positions",).annotate(
            total=Sum(
                F("warehouse_order_positions__quantity")
                * F("warehouse_order_positions__buying_price")
            )
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


class PersonnelDocumentViewSet(BulkChangeArchiveStatusViewSetMixin, ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.PersonnelDocumentSerializer
    lookup_field = "id"
    queryset = models.PersonnelDocument.objects.all()


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


class CreateProductionDocumentException(APIException):
    status_code = HTTP_409_CONFLICT


class ProductionDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (AllowAny,)
    queryset = models.ProductionDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.ProductionDocumentSerializer

    @staticmethod
    def get_or_create_warehouse(shop, product_unit, **kwargs):
        return models.Warehouse.objects.get_or_create(
            shop=shop,
            product_unit_id=product_unit,
            defaults=kwargs,
        )[0]

    @transaction.atomic()
    def perform_create(self, serializer):
        # try to write off the ingredients and register the produce
        menu = serializer.validated_data.get("daily_menu_plan")
        ingredients = menu._meta.model.layout.filter(id=menu.id)
        if ingredients.filter(shortage__gt=0).exists():
            # missing some ingredients
            view_url = reverse("production:dailymenuplan-layout", args=[menu.id])
            raise CreateProductionDocumentException(
                detail={"url": f"{view_url}?shortage=true"},
                code="Недостаточно сырья",
            )

        document = serializer.save()

        write_offs = []
        for ingredient in ingredients:
            write_offs.append(
                models.WarehouseRecord(
                    document=document,
                    # there should be a better method of getting `warehouse_id`
                    # considering the `Warehouse` object must exist at this
                    # point (via the ingredient query?)
                    warehouse=self.get_or_create_warehouse(
                        menu.shop,
                        ingredient["dishes__tech_products__product_unit"],
                    ),
                    quantity=-ingredient["total"],
                )
            )
        models.WarehouseRecord.objects.bulk_create(write_offs)

        # register the produce
        produce = []
        for end_product in menu._meta.model.produce.filter(id=menu.id):
            produce.append(
                models.WarehouseRecord(
                    document=document,
                    warehouse=self.get_or_create_warehouse(
                        menu.shop,
                        end_product["dishes__end_product"],
                    ),
                    quantity=end_product["produce"],
                )
            )
        models.WarehouseRecord.objects.bulk_create(produce)


@method_decorator(transaction.atomic, "perform_create")
class InventoryDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (AllowAny,)
    queryset = models.InventoryDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.InventoryDocumentSerializer


@method_decorator(transaction.atomic, "perform_create")
class WriteOffDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (AllowAny,)
    queryset = models.WriteOffDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.WriteOffDocumentSerializer


@method_decorator(transaction.atomic, "perform_create")
class ConversionDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (AllowAny,)
    queryset = models.ConversionDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.ConversionDocumentSerializer


@method_decorator(transaction.atomic, "perform_create")
class MoveDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (AllowAny,)
    queryset = models.MoveDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.MoveDocumentSerializer


@method_decorator(transaction.atomic, "perform_create")
class ReceiptDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (AllowAny,)
    queryset = models.ReceiptDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.ReceiptDocumentSerializer


@method_decorator(transaction.atomic, "perform_create")
class SaleDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (AllowAny,)
    queryset = models.SaleDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.SaleDocumentSerializer


class CancelDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (AllowAny,)
    queryset = models.CancelDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.CancelDocumentSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        document = serializer.save()
        records = []
        for item in document.cancels.warehouse_records.all():
            # create a record that cancels a record from the document
            # being cancelled:
            records.append(
                models.WarehouseRecord(
                    warehouse=item.warehouse,
                    quantity=-item.quantity,
                    document=document,
                )
            )
        models.WarehouseRecord.objects.bulk_create(records)
