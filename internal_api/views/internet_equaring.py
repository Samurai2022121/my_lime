from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Order
from orders.serializers import OrdersSerializer
from utils.merchant import merchant


class OrderPayView(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = []
    http_method_names = ["get", "head"]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        res = merchant.registration_order(instance)
        order_id = res.get("orderId")
        instance.payment_status = order_id
        instance.save()
        return Response(res)
