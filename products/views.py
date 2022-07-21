from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_nested.viewsets import NestedViewSetMixin

from utils import permissions as perms
from utils.views_utils import (
    BulkChangeArchiveStatusViewSetMixin,
    BulkUpdateViewSetMixin,
    ChangeDestroyToArchiveMixin,
    OrderingModelViewsetMixin,
)

from . import serializers
from .filters import CategoryFilter, ProductFilter, ProductUnitFilter
from .models import (
    Category,
    MeasurementUnit,
    Product,
    ProductImage,
    ProductUnit,
    ProductUnitConversion,
)


class MeasurementUnitViewset(viewsets.ModelViewSet):
    permission_classes = (
        perms.ReadWritePermission(read=perms.allow_all, write=perms.allow_staff),
    )
    queryset = MeasurementUnit.objects.order_by("name")
    serializer_class = serializers.MeasurementUnitSerializer


class ProductAdminViewset(
    BulkChangeArchiveStatusViewSetMixin,
    ChangeDestroyToArchiveMixin,
    BulkUpdateViewSetMixin,
    OrderingModelViewsetMixin,
    viewsets.ModelViewSet,
):
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_all,
            write=perms.allow_staff,
            bulk_update=perms.allow_staff,
            change_archive_status=perms.allow_staff,
        ),
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter
    serializer_class = serializers.ProductAdminSerializer
    serializer_action_classes = {
        "list": serializers.ProductListAdminSerializer,
        "change_category": serializers.BulkChangeProductCategorySerializer,
    }
    lookup_field = "id"
    queryset = Product.objects.all()

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action, super().get_serializer_class()
        )

    def get_object(self):
        return self.queryset.get(id=self.kwargs["id"])

    def get_queryset(self):
        qs = self.queryset
        query_params = self.request.query_params
        if "is_sorted" not in query_params:
            qs = qs.filter(is_sorted=True)
        if "is_archive" not in query_params:
            qs = qs.filter(is_archive=False)

        ordering_fields = self.get_ordering_fields()
        if ordering_fields:
            return qs.order_by(*ordering_fields)
        return qs.order_by("name")

    @action(detail=False, methods=["post"], url_path="bulk-change-category")
    def change_category(self, request, **kwargs):
        serializer = self.get_serializer_class()
        serialized_data = serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        product_ids = serialized_data.data["product_ids"]
        new_category = serialized_data.data["new_category"]
        Product.objects.filter(id__in=product_ids).update(category=new_category)
        return Response(status=status.HTTP_200_OK)


class ProductUnitViewset(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (
        perms.ReadWritePermission(read=perms.allow_all, write=perms.allow_staff),
    )
    serializer_class = serializers.ProductUnitSerializer
    queryset = ProductUnit.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductUnitFilter
    lookup_field = "id"
    parent_lookup_kwargs = {"product_id": "product__id"}

    def perform_create(self, serializer):
        serializer.save(**self.kwargs)


class ConversionSourceViewset(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (
        perms.ReadWritePermission(read=perms.allow_all, write=perms.allow_staff),
    )
    serializer_class = serializers.ConversionSourceSerializer
    queryset = ProductUnitConversion.objects.order_by("target_unit__unit__name")
    lookup_field = "id"
    parent_lookup_kwargs = {
        "product_id": "source_unit__product_id",
        "unit_id": "source_unit",
    }

    def perform_create(self, serializer):
        serializer.save(target_unit_id=self.kwargs.get("unit_id", None))


class ConversionTargetViewset(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (
        perms.ReadWritePermission(read=perms.allow_all, write=perms.allow_staff),
    )
    serializer_class = serializers.ConversionTargetSerializer
    queryset = ProductUnitConversion.objects.order_by("source_unit__unit__name")
    lookup_field = "id"
    parent_lookup_kwargs = {
        "product_id": "target_unit__product_id",
        "unit_id": "target_unit",
    }

    def perform_create(self, serializer):
        serializer.save(source_unit_id=self.kwargs.get("unit_id", None))


class ProductViewset(
    OrderingModelViewsetMixin,
    viewsets.ReadOnlyModelViewSet,
):
    permission_classes = (perms.ReadWritePermission(read=perms.allow_all),)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter
    serializer_class = serializers.ProductSerializer
    serializer_action_classes = {
        "list": serializers.ProductListSerializer,
    }
    lookup_field = "id"
    queryset = Product.objects.all()

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action, super().get_serializer_class()
        )

    def get_object(self):
        return self.queryset.get(id=self.kwargs["id"])

    def get_queryset(self):
        qs = self.queryset.filter(
            is_archive=False, is_sorted=True, own_production=False
        )
        ordering_fields = self.get_ordering_fields()
        if ordering_fields:
            return qs.order_by(*ordering_fields)
        return qs.order_by("name")


class CategoryViewset(BulkChangeArchiveStatusViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_all,
            write=perms.allow_staff,
            change_archive_status=perms.allow_staff,
        ),
    )
    pagination_class = None
    serializer_class = serializers.CategorySerializer
    lookup_field = "id"
    serializer_action_classes = {
        "list": serializers.CategoryListSerializer,
        "retrieve": serializers.CategoryListSerializer,
    }
    queryset = Category.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CategoryFilter

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action, super().get_serializer_class()
        )

    def get_object(self):
        return self.queryset.get(id=self.kwargs["id"])

    def get_queryset(self):
        main_categories = self.queryset.filter(level=0)
        qs = Category.objects.get_queryset_descendants(
            main_categories, include_self=True
        ).filter(level=0)

        if "s" in self.request.query_params:
            search_value = self.request.query_params["s"]
            qs = self.queryset.filter(Q(name__icontains=search_value))

        return qs


class EditProductImagesViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (
        perms.ActionPermission(
            list=perms.allow_all,
            create=perms.allow_staff,
            bulk_update=perms.allow_staff,
            bulk_delete=perms.allow_staff,
        ),
    )
    pagination_class = None
    serializer_class = serializers.EditProductImageSerializer
    queryset = ProductImage.objects.all()
    serializer_action_classes = {
        "bulk_update": serializers.BulkUpdateProductImageSerializer,
        "create": serializers.BulkEditProductImageSerializer,
        "bulk_delete": serializers.BulkActionProductImageSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action, super().get_serializer_class()
        )

    def get_queryset(self):
        product_id = self.request.query_params.get("product_id", 0)
        return self.queryset.filter(product=product_id)

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        for image in data["images"]:
            ProductImage.objects.create(**image)
        return Response(serializer_class(data).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="bulk_update")
    def bulk_update(self, request, **kwargs):
        serializer = self.get_serializer_class()
        serialized_data = serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        instances = serialized_data.data["instances"]
        product = Product.objects.get(id=serialized_data.data["product"])
        for instance in instances:
            image = self.queryset.filter(id=instance.pop("id", None))
            if image:
                image.update(**instance)
            else:
                ProductImage.objects.create(**instance, product=product)
        return Response(status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request, **kwargs):
        serializer = self.get_serializer_class()
        serialized_data = serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        image_ids = serialized_data.data["image_ids"]
        ProductImage.objects.filter(id__in=image_ids).delete()
        return Response(status=status.HTTP_200_OK)
