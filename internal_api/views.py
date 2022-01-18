import pandas as pd
from django.db.models import F, Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST

from products.models import Product
from utils.serializers_utils import BulkUpdateSerializer
from utils.views_utils import (BulkChangeArchiveStatusViewSetMixin,
                               BulkUpdateViewSetMixin,
                               ChangeDestroyToArchiveMixin)

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
            qs = qs.filter(shop=outlet_id)
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
        serialized_data = self.serializer_class(data=request.data)
        serialized_data.is_valid(raise_exception=True)

        file = pd.read_excel(serialized_data["csv_file"])
        file = file.where(pd.notnull(file), None)
        products = []
        for index, row in file.iloc[serialized_data["first_row"] :].iterrows():
            if not (name := row[serialized_data["name_col"]]) and not (
                price := row[serialized_data["price_col"]]
            ):
                continue
            products.append(
                Product(
                    name=name,
                    price=price,
                    barcode=row[serialized_data["barcode"]],
                    vat_value=row[serialized_data["vat_col"]],
                    measure_unit=row[serialized_data["measure_unit_col"]],
                    origin=row[serialized_data["origin_col"]],
                    manufacturer=row[serialized_data["supplier_col"]],
                )
            )
        created_products = Product.objects.bulk_create(products)

        return Response(status=HTTP_202_ACCEPTED, data=created_products)


class WarehouseOrderViewSet(ChangeDestroyToArchiveMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.WarehouseOrderSerializer
    lookup_field = "id"
    queryset = models.WarehouseOrder.objects.all()

    def get_queryset(self):
        qs = (
            self.queryset.prefetch_related("warehouse_order")
            .filter(is_archieve=False)
            .annotate(
                total=Sum(
                    F("warehouse_order__quantity") * F("warehouse_order__buying_price")
                )
            )
        )
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


class SupplyContractViewSet(BulkChangeArchiveStatusViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.SupplyContractSerializer
    lookup_field = "id"
    queryset = models.SupplyContract.objects.all()
