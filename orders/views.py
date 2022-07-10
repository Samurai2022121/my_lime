from rest_framework.viewsets import ReadOnlyModelViewSet

from utils import permissions as perms

from .models import Order
from .serializers import OrdersSerializer


class OrderViewset(ReadOnlyModelViewSet):
    # web store client is allowed to create order from basket,
    # not to screw it afterwards
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_authenticated,
        ),
    )
    serializer_class = OrdersSerializer
    lookup_field = "id"
    queryset = Order.objects.all()

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if not (user.is_superuser or user.is_staff):
            qs = qs.filter(buyer=user)
        return qs
