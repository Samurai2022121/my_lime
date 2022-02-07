from decimal import Decimal

import pandas as pd
from django.db.models import F, Q, Sum
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST, HTTP_201_CREATED

from products.models import Product
from products.serializers import ProductListSerializer
from utils.serializers_utils import BulkUpdateSerializer
from utils.views_utils import (
    BulkChangeArchiveStatusViewSetMixin,
    BulkUpdateViewSetMixin,
    ChangeDestroyToArchiveMixin,
)

from . import models, serializers


class ShopViewSet(
    ChangeDestroyToArchiveMixin,
    BulkChangeArchiveStatusViewSetMixin,
    BulkUpdateViewSetMixin,
    viewsets.ModelViewSet,
):
    permission_classes = (AllowAny,)
    serializer_class = serializers.ShopSerializer
    lookup_field = "id"
    queryset = models.Shop.objects.all()

    def get_queryset(self):
        qs = self.queryset
        if "s" in self.request.query_params:
            search_value = self.request.query_params["s"]
            qs = qs.filter(
                Q(name__icontains=search_value)
                | Q(address__icontains=search_value)
                | Q(id__icontains=search_value)
            )
        return qs


class PersonnelViewSet(
    ChangeDestroyToArchiveMixin,
    BulkChangeArchiveStatusViewSetMixin,
    viewsets.ModelViewSet,
):
    permission_classes = (AllowAny,)
    serializer_class = serializers.PersonnelSerializer
    lookup_field = "id"
    queryset = models.Personnel.objects.all()


class WarehouseViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.WarehouseSerializer
    lookup_field = "id"
    queryset = models.Warehouse.objects.all()

    def get_queryset(self):
        qs = self.queryset
        outlet_id = self.request.query_params.get("outlet", None)
        if outlet_id:
            qs = qs.filter(shop=outlet_id, product__is_archive=False)
        else:
            qs = qs.none()
        if "s" in self.request.query_params:
            search_value = self.request.query_params["s"]
            qs = qs.filter(
                Q(product__name__icontains=search_value)
                | Q(product__barcode__icontains=search_value)
                | Q(product__id__icontains=search_value)
            )
        qs = qs.order_by("product__name")
        return qs

    @action(detail=False, methods=["post"], url_path="bulk_update")
    def bulk_update(self, request, **kwargs):
        serialized_data = BulkUpdateSerializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        instances = serialized_data.data["instances"]
        for instance in instances:
            image_id = instance.pop("id", None)
            product_id = instance.pop("product")
            if not product_id:
                return Response(
                    status=HTTP_400_BAD_REQUEST, data={"message": "Товар не существует"}
                )
            product = Product.objects.get(id=product_id)
            instance.update({"product": product})
            if image_id:
                self.queryset.filter(id=image_id).update(**instance)
            else:
                models.Warehouse.objects.create(**instance)
        return Response(status=HTTP_202_ACCEPTED)


class UploadCSVGenericView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.UploadCSVSerializer
    queryset = models.Product.objects.all()

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

        for index, row in file.iloc[row_num:].iterrows():

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
                        if data.get("measure_unit_col", None)
                        else None,
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


class WarehouseOrderViewSet(ChangeDestroyToArchiveMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.WarehouseOrderSerializer
    lookup_field = "id"
    queryset = models.WarehouseOrder.objects.all()

    def get_queryset(self):
        qs = (
            self.queryset.prefetch_related("warehouse_order")
            .filter(is_archive=False)
            .annotate(
                total=Sum(
                    F("warehouse_order__quantity") * F("warehouse_order__buying_price")
                )
            )
        )
        if "s" in self.request.query_params:
            search_value = self.request.query_params["s"]
            qs = qs.filter(Q(order_number__icontains=search_value))
        return qs


class SupplierViewSet(
    ChangeDestroyToArchiveMixin,
    BulkChangeArchiveStatusViewSetMixin,
    BulkUpdateViewSetMixin,
    viewsets.ModelViewSet,
):
    permission_classes = (AllowAny,)
    serializer_class = serializers.SupplierSerializer
    lookup_field = "id"
    queryset = models.Supplier.objects.all()

    def get_queryset(self):
        qs = self.queryset
        if "s" in self.request.query_params:
            search_value = self.request.query_params["s"]
            qs = qs.filter(
                Q(name__icontains=search_value)
                | Q(email__icontains=search_value)
                | Q(phone__icontains=search_value)
            )
        return qs.order_by("name")


class SupplyContractViewSet(BulkChangeArchiveStatusViewSetMixin, viewsets.ModelViewSet):
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


class PersonnelDocumentViewSet(
    BulkChangeArchiveStatusViewSetMixin, viewsets.ModelViewSet
):
    permission_classes = (AllowAny,)
    serializer_class = serializers.PersonnelDocumentSerializer
    lookup_field = "id"
    queryset = models.PersonnelDocument.objects.all()


class TechCardViewSet(BulkChangeArchiveStatusViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.TechCardSerializer
    lookup_field = "id"
    queryset = models.TechCard.objects.filter(is_archive=False)


class DailyMenuViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.DailyMenuSerializer
    lookup_field = "id"
    queryset = models.DailyMenuPlan.objects.all()


class LegalEntityFilterSet(filters.FilterSet):
    """Searches through `registration_id` and/or `name` fields."""

    s = filters.CharFilter(
        method="search_by_id_or_name",
        label="регистрационный номер или наименование",
    )

    class Meta:
        model = models.LegalEntities
        fields = ("s",)

    def search_by_id_or_name(self, qs, name, value):
        return qs.filter(Q(registration_id__contains=value) | Q(name__icontains=value))


class LegalEntityViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.LegalEntitySerializer
    lookup_field = "registration_id"
    queryset = models.LegalEntities.objects.filter(active="+")
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = LegalEntityFilterSet

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paginator.page_size = 30
