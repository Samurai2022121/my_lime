from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from utils.views_utils import (
    BulkChangeArchiveStatusViewSetMixin,
    OrderingModelViewsetMixin,
)

from .models import Order
from .serializers import OrdersSerializer
from .filters import OrderFilter


class OrderViewset(
    BulkChangeArchiveStatusViewSetMixin,
    OrderingModelViewsetMixin,
    viewsets.ModelViewSet,
):
    filterset_class = OrderFilter
    permission_classes = (AllowAny,)
    serializer_class = OrdersSerializer
    lookup_field = "id"
    queryset = Order.objects.all()

    def get_object(self):
        return self.queryset.get(id=self.kwargs["id"])

    def get_queryset(self):
        qs = self.queryset

        if "is_archive" not in self.request.query_params:
            qs = qs.filter(is_archive=False)

        ordering_fields = self.get_ordering_fields()
        if ordering_fields:
            return qs.order_by(*ordering_fields)
        return qs
