from rest_framework import viewsets

from utils import permissions as perms
from utils.views_utils import (
    BulkChangeArchiveStatusViewSetMixin,
    OrderingModelViewsetMixin,
)

from .filters import OrderFilter
from .models import Order
from .serializers import OrdersSerializer


class OrderViewset(
    BulkChangeArchiveStatusViewSetMixin,
    OrderingModelViewsetMixin,
    viewsets.ModelViewSet,
):
    filterset_class = OrderFilter
    # web store client is allowed to create order, not to screw it afterwards
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_authenticated,
            create=perms.allow_authenticated,
            write=perms.allow_staff,
            change_archive_status=perms.allow_staff,
        ),
    )
    serializer_class = OrdersSerializer
    lookup_field = "id"
    queryset = Order.objects.all()

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user

        if not (user.is_superuser or user.is_staff):
            qs = qs.filter(customer=user)

        if "is_archive" not in self.request.query_params:
            qs = qs.filter(is_archive=False)

        ordering_fields = self.get_ordering_fields()
        if ordering_fields:
            return qs.order_by(*ordering_fields)
        return qs
