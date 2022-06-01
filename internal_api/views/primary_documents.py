from django.db import transaction
from django.utils.decorators import method_decorator
from django_filters import rest_framework as df_filters
from rest_framework.exceptions import APIException
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_409_CONFLICT
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin

from utils import permissions as perms

from .. import filters, models, serializers


class CreateProductionDocumentException(APIException):
    status_code = HTTP_409_CONFLICT


def allow_staff_or_buyer(perm, request, view):
    # allow e-commerce site users to view only sale document records
    if view.basename == "salerecord":
        return request.user.is_authenticated
    else:
        return request.user.is_staff


class PrimaryDocumentRecordViewSet(NestedViewSetMixin, ReadOnlyModelViewSet):
    permission_classes = (perms.ReadWritePermission(read=allow_staff_or_buyer),)
    queryset = models.WarehouseRecord.objects.order_by(
        "warehouse__product_unit__product__name",
    )
    serializer_class = serializers.WarehouseRecordSerializer
    lookup_field = "id"
    parent_lookup_kwargs = {"document_id": "document__id"}


class ProductionDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_staff,
            create=perms.allow_staff,
            destroy=perms.allow_staff,
        ),
    )
    queryset = models.ProductionDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.ProductionDocumentSerializer
    lookup_field = "id"
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.PrimaryDocumentFilter

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
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_staff,
            create=perms.allow_staff,
            destroy=perms.allow_staff,
        ),
    )
    queryset = models.InventoryDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.InventoryDocumentSerializer
    lookup_field = "id"
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.PrimaryDocumentFilter


@method_decorator(transaction.atomic, "perform_create")
class WriteOffDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_staff,
            create=perms.allow_staff,
            destroy=perms.allow_staff,
        ),
    )
    queryset = models.WriteOffDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.WriteOffDocumentSerializer
    lookup_field = "id"
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.PrimaryDocumentFilter


@method_decorator(transaction.atomic, "perform_create")
class ReturnDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_staff,
            create=perms.allow_staff,
            destroy=perms.allow_staff,
        ),
    )
    queryset = models.ReturnDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.ReturnDocumentSerializer
    lookup_field = "id"
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.PrimaryDocumentFilter


@method_decorator(transaction.atomic, "perform_create")
class ConversionDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_staff,
            create=perms.allow_staff,
            destroy=perms.allow_staff,
        ),
    )
    queryset = models.ConversionDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.ConversionDocumentSerializer
    lookup_field = "id"
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.PrimaryDocumentFilter


@method_decorator(transaction.atomic, "perform_create")
class MoveDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_staff,
            create=perms.allow_staff,
            destroy=perms.allow_staff,
        ),
    )
    queryset = models.MoveDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.MoveDocumentSerializer
    lookup_field = "id"
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.PrimaryDocumentFilter


@method_decorator(transaction.atomic, "perform_create")
class ReceiptDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_staff,
            create=perms.allow_staff,
            destroy=perms.allow_staff,
        ),
    )
    queryset = models.ReceiptDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.ReceiptDocumentSerializer
    lookup_field = "id"
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.PrimaryDocumentFilter


@method_decorator(transaction.atomic, "perform_create")
class SaleDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_authenticated,
            create=perms.allow_authenticated,
            destroy=perms.allow_staff,
        ),
    )
    queryset = models.SaleDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.SaleDocumentSerializer
    lookup_field = "id"
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.PrimaryDocumentFilter

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return qs

        return qs.filter(author=user)


class CancelDocumentViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_staff,
            create=perms.allow_staff,
            destroy=perms.allow_staff,
        ),
    )
    queryset = models.CancelDocument.objects.order_by("created_at", "number")
    serializer_class = serializers.CancelDocumentSerializer
    lookup_field = "id"
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.PrimaryDocumentFilter

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
                    batch=item.batch,
                    cost=item.cost,
                    document=document,
                )
            )
        models.WarehouseRecord.objects.bulk_create(records)
