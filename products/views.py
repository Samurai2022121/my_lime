from django.db.models import Q
from rest_framework import viewsets, exceptions
from rest_framework.permissions import IsAuthenticated, AllowAny

from utils.views_utils import ProductPagination

from .models import Category, Product
from .serializers import ProductListSerializer, ProductSerializer, CategoryListSerializer, CategorySerializer


class ProductViewset(viewsets.ModelViewSet):
    pagination_class = ProductPagination
    permission_classes = (AllowAny,)
    serializer_class = ProductSerializer
    serializer_action_classes = {
        'list': ProductListSerializer
    }
    lookup_field = 'id'
    queryset = Product.objects.all()

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, super().get_serializer_class())

    def get_object(self):
        return self.queryset.get(id=self.kwargs['id'])

    def get_queryset(self):
        qs = self.queryset
        if 's' in self.request.query_params:
            search_value = self.request.query_params['s']
            qs = qs.filter(Q(name__icontains=search_value) | Q(barcode__icontains=search_value))
        return qs.order_by(
            'in_stock'
        )

    # def create(self, request, *args, **kwargs):
    #     raise exceptions.ValidationError('CREATE is not supported')
    #
    # def destroy(self, request, *args, **kwargs):
    #     raise exceptions.ValidationError('DELETE is not supported')


class CategoryViewset(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = CategorySerializer
    lookup_field = 'id'
    serializer_action_classes = {
        'list': CategoryListSerializer
    }
    queryset = Category.objects.all()

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, super().get_serializer_class())

    def get_object(self):
        return self.queryset.get(id=self.kwargs['id'])

    def get_queryset(self):
        return self.queryset.get_cached_trees()
