from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Order, PaymentResult
from orders.serializers import OrderSerializer
from utils.merchant import merchant


class OrderPayView(viewsets.ModelViewSet):
    queryset = Order.objects
    serializer_class = OrderSerializer
    permission_classes = []
    http_method_names = ["get", "head"]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        res = merchant.registration_order(instance)
        bank_order_id = res.get("orderId")
        PaymentResult.objects.create(
            order=instance,
            bank_order_id=bank_order_id,
            payment_status=0,
            amount=sum([line.order_line.full_price for line in instance.lines.all()]),
        )
        return Response(res)
