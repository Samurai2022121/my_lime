from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from utils.serializers_utils import BulkUpdateSerializer
from utils.views_utils import (BulkUpdateViewSetMixin,
                               OrderingModelViewsetMixin, ProductPagination)

from . import serializers
from .filters import ProductFilter
from .models import Category, Product, ProductImages


class ProductViewset(
    BulkUpdateViewSetMixin, OrderingModelViewsetMixin, viewsets.ModelViewSet
):
    pagination_class = ProductPagination
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter
    serializer_class = serializers.ProductSerializer
    serializer_action_classes = {
        "list": serializers.ProductListSerializer,
        "change_archive_status": serializers.BulkActionProductSerializer,
        "change_category": serializers.BulkChangeProductCategorySerializer,
        "bulk_delete": serializers.BulkActionProductSerializer,
        "bulk_update": BulkUpdateSerializer,
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

    @action(detail=False, methods=["post"], url_path="bulk-archive")
    def change_archive_status(self, request, **kwargs):
        serializer = self.get_serializer_class()
        serialized_data = serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        product_ids = serialized_data.data["product_ids"]
        Product.objects.filter(id__in=product_ids).update(
            is_archive=Q(is_archive=False)
        )
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="bulk-change-category")
    def change_category(self, request, **kwargs):
        serializer = self.get_serializer_class()
        serialized_data = serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        product_ids = serialized_data.data["product_ids"]
        new_category = serialized_data.data["new_category"]
        Product.objects.filter(id__in=product_ids).update(category=new_category)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request, **kwargs):
        serializer = self.get_serializer_class()
        serialized_data = serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        product_ids = serialized_data.data["product_ids"]
        Product.objects.filter(id__in=product_ids).delete()
        return Response(status=status.HTTP_200_OK)


class CategoryViewset(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
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
        return self.queryset.get_cached_trees()


class EditProductImagesViewset(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (AllowAny,)
    lookup_field = "id"
    serializer_class = serializers.EditProductImagesSerializer
    queryset = ProductImages.objects.all()

    def get_object(self):
        return self.queryset.get(id=self.kwargs["id"])
