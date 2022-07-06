from django.db.models import F
from django_filters import rest_framework as df_filters
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin

from products.models import Category
from utils import permissions as perms
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
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_staff,
            write=perms.allow_staff,
            change_archive_status=perms.allow_staff,
            bulk_update=perms.allow_staff,
        ),
    )
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


def allow_all_for_e_shop(perm, request, view):
    """
    Allow access to ecommerce warehouses for all. Limit access to other
    warehouses to staff.
    """
    shop = get_object_or_404(
        models.Shop.objects.all(),
        id=request.query_params.get("shop"),
    )
    return shop.e_shop_base or perms.allow_staff(perm, request, view)


class WarehouseViewSet(NestedViewSetMixin, ModelViewSet):
    permission_classes = (
        perms.ReadWritePermission(read=allow_all_for_e_shop, write=perms.allow_staff),
    )
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
    permission_classes = (
        perms.ReadWritePermission(read=perms.allow_staff, write=perms.allow_staff),
    )
    serializer_class = serializers.WarehouseRecordSerializer
    lookup_field = "id"
    parent_lookup_kwargs = {
        "shop_id": "warehouse__shop_id",
        "warehouse_id": "warehouse__id",
    }
    queryset = models.WarehouseRecord.objects.prefetch_related(
        "batch", "batch__supplier"
    ).order_by("-updated_at")

    def get_serializer_class(self):
        serializer_class = super().get_serializer_class()
        if self.request.method == "get":
            serializer_class = exclude_field(serializer_class, "warehouse")
        return serializer_class

    def perform_create(self, serializer):
        serializer.save(
            warehouse_id=self.kwargs.get("warehouse_id", None),
        )


class WarehouseForScalesListView(NestedViewSetMixin, ReadOnlyModelViewSet):
    permission_classes = (perms.ReadWritePermission(read=perms.allow_staff),)
    pagination_class = None
    serializer_class = serializers.WarehouseForScalesSerializer
    queryset = models.Warehouse.objects
    parent_lookup_kwargs = {"shop_id": "shop__id"}

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related(
            "product_unit", "product_unit__unit", "product_unit__product"
        )
        qs = qs.annotate(
            category_id=F("product_unit__product__category__id"),
            category_name=F("product_unit__product__category__name"),
        )
        return qs

    # TODO: Использовать сериалайзер, оптимизировать запрос;
    def list(self, request, *args, **kwargs):
        response = super(WarehouseForScalesListView, self).list(
            self, request, *args, **kwargs
        )
        new_response = dict()
        categories_dict = {}
        categories = Category.objects.filter(level=0)
        for category in categories:
            category_children = category.get_descendants(include_self=True).values_list(
                "id", flat=True
            )
            categories_dict.update({category.id: list(category_children)})
        for i in response.data:
            parent_category = None
            for category in categories_dict:
                if i["category_id"] in categories_dict[category]:
                    parent_category = category
                    break
            if parent_category not in new_response:
                new_response.update({parent_category: [i]})
            else:
                new_response[parent_category].append(i)
        return Response(data=new_response)


class BatchViewSet(ModelViewSet):
    permission_classes = (
        perms.ReadWritePermission(read=perms.allow_staff, write=perms.allow_staff),
    )
    lookup_field = "id"
    serializer_class = serializers.BatchSerializer
    filter_backends = (df_filters.DjangoFilterBackend,)
    filterset_class = filters.BatchFilter
    queryset = models.Batch.objects.order_by("created_at")
