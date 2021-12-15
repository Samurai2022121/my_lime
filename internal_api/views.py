from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from django.db.models import Q, OuterRef

from products.models import Product

from . import models, serializers


class ShopViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.ShopSerializer
    lookup_field = "id"
    queryset = models.Shop.objects.all()


class PersonnelViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.PersonnelSerializer
    lookup_field = "id"
    queryset = models.Personnel.objects.all()


class WarehouseViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.WarehouseSerializer
    lookup_field = "id"
    queryset = Product.objects.all()

    # def get_queryset(self):
    #     qs = self.queryset
    #     qs = qs.annotate(
    #
    #     )
    #     return qs
