from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from utils.views_utils import (
    BulkChangeArchiveStatusViewSetMixin,
    OrderingModelViewsetMixin,
)

from .models import Order
from .serializers import OrdersSerializer


class OrderViewset(
    BulkChangeArchiveStatusViewSetMixin,
    OrderingModelViewsetMixin,
    viewsets.ModelViewSet,
):
    permission_classes = (AllowAny,)
    serializer_class = OrdersSerializer
    lookup_field = "id"
    queryset = Order.objects.all()

    def get_object(self):
        return self.queryset.get(id=self.kwargs["id"])

    def get_queryset(self):
        qs = self.queryset
        if "s" in self.request.query_params:
            search_value = self.request.query_params["s"]
            qs = qs.filter(
                Q(customer__surname__icontains=search_value)
                | Q(id__icontains=search_value)
                | Q(customer__phone_number__icontains=search_value)
            )
        ordering_fields = self.get_ordering_fields()
        if ordering_fields:
            return qs.order_by(*ordering_fields)
        return qs
