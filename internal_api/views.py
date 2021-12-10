from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from . import models, serializers


class ShopViewset(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.ShopSerializer
    lookup_field = "id"
    queryset = models.Shop.objects.all()
