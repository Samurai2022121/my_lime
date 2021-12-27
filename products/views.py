from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from internal_api.models import Warehouse
from utils.serializers_utils import BulkUpdateSerializer
from utils.views_utils import (BulkChangeArchiveStatusViewSetMixin,
                               BulkUpdateViewSetMixin,
                               ChangeDestroyToArchiveMixin,
                               OrderingModelViewsetMixin)

from . import serializers
from .filters import ProductFilter
from .models import Category, Product, ProductImages


class ProductViewset(
    BulkChangeArchiveStatusViewSetMixin,
    ChangeDestroyToArchiveMixin,
    BulkUpdateViewSetMixin,
    OrderingModelViewsetMixin,
    viewsets.ModelViewSet,
):
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter
    serializer_class = serializers.ProductSerializer
    serializer_action_classes = {
        "list": serializers.ProductListSerializer,
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
        qs = self.queryset.filter(is_archive=False)
        if "s" in self.request.query_params:
            search_value = self.request.query_params["s"]
            qs = qs.filter(
                Q(name__icontains=search_value) | Q(barcode__icontains=search_value)
            )
        ordering_fields = self.get_ordering_fields()
        if ordering_fields:
            return qs.order_by(*ordering_fields)
        return qs.order_by("in_stock")

    @action(detail=False, methods=["post"], url_path="bulk-change-category")
    def change_category(self, request, **kwargs):
        serializer = self.get_serializer_class()
        serialized_data = serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        product_ids = serialized_data.data["product_ids"]
        new_category = serialized_data.data["new_category"]
        Product.objects.filter(id__in=product_ids).update(category=new_category)
        return Response(status=status.HTTP_200_OK)


class CategoryViewset(BulkChangeArchiveStatusViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    pagination_class = None
    serializer_class = serializers.CategorySerializer
    lookup_field = "id"
    serializer_action_classes = {"list": serializers.CategoryListSerializer}
    queryset = Category.objects.all()

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action, super().get_serializer_class()
        )

    def get_object(self):
        return self.queryset.get(id=self.kwargs["id"])

    def get_queryset(self):
        main_categories = self.queryset.filter(level=0)
        return Category.objects.get_queryset_descendants(
            main_categories, include_self=True
        ).filter(level=0)


class EditProductImagesViewset(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (AllowAny,)
    pagination_class = None
    serializer_class = serializers.EditProductImagesSerializer
    queryset = ProductImages.objects.all()
    serializer_action_classes = {
        "bulk_update": BulkUpdateSerializer,
        "create": serializers.BulkEditProductImagesSerializer,
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
        serializer = self.get_serializer_class()
        serialized_data = serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        for image in serialized_data:
            ProductImages.objects.create(**image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="bulk_update")
    def bulk_update(self, request, **kwargs):
        serializer = self.get_serializer_class()
        serialized_data = serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        instances = serialized_data.data["instances"]
        for instance in instances:
            image = self.queryset.filter(id=instance.pop("id", None))
            if image:
                image.update(**instance)
            else:
                ProductImages.objects.create(**instance)
        return Response(status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request, **kwargs):
        serializer = self.get_serializer_class()
        serialized_data = serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        image_ids = serialized_data.data["image_ids"]
        ProductImages.objects.filter(id__in=image_ids).delete()
        return Response(status=status.HTTP_200_OK)


class ProductMatrixViewset(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.ProductMatrixSerializer
    queryset = Product.objects.all()

    def get_queryset(self):
        qs = self.queryset
        outlet_id = self.request.query_params.get("outlet", None)
        outlet_products_ids = Warehouse.objects.filter(shop=outlet_id).values_list(
            "product__id", flat=True
        )
        if outlet_products_ids:
            qs = self.queryset.exclude(id__in=outlet_products_ids)
        return qs
