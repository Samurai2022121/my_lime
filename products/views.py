from rest_framework import viewsets, exceptions
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny

from products.models import Category, Product
from products.serializers import CategorySerializer, ProductListSerializer, ProductSerializer


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


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
        return self.queryset.order_by(
            'in_stock'
        )

    def create(self, request, *args, **kwargs):
        raise exceptions.ValidationError('CREATE is not supported')

    def destroy(self, request, *args, **kwargs):
        raise exceptions.ValidationError('DELETE is not supported')
