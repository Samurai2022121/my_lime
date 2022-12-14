from typing import AnyStr, Dict, Union

from django.db.models import DecimalField, QuerySet, Sum
from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views.generic import View
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin

from basket.views import OfferMixin
from utils import permissions as perms
from utils.merchant import merchant

from .models import Order, OrderLine, OrderLineOffer, PaymentResult
from .serializers import (
    NestedOrderLineSerializer,
    NestedOrderSerializer,
    OrderFromBasketSerializer,
    OrderLineOfferSerializer,
    OrderSerializer,
)


class OrderLineOfferViewset(NestedViewSetMixin, ModelViewSet):
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_authenticated,
            write=perms.allow_staff,
        ),
    )
    serializer_class = OrderLineOfferSerializer
    lookup_field = "id"
    queryset = OrderLineOffer.objects.all()
    parent_lookup_kwargs = {
        "line_id": "line__id",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not (user.is_superuser or user.is_staff):
            qs = qs.filter(buyer=user)
        return qs


class OrderLineViewset(NestedViewSetMixin, ModelViewSet):
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_authenticated,
            write=perms.allow_staff,
        ),
    )
    serializer_class = NestedOrderLineSerializer
    lookup_field = "id"
    queryset = OrderLine.objects.all()
    parent_lookup_kwargs = {
        "order_id": "document__id",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not (user.is_superuser or user.is_staff):
            qs = qs.filter(buyer=user)
        return qs


class OrderViewset(OfferMixin, ModelViewSet):
    # web store client is allowed to create order from basket,
    # not to screw it afterwards
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_authenticated,
            write=perms.allow_staff,
            from_basket=perms.allow_authenticated,
        ),
    )
    serializer_class = NestedOrderSerializer
    lookup_field = "id"
    queryset = Order.objects.all()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        # just created `Order` instance lacks annotated fields,
        # but `Order.shop` annotation is necessary at this point
        serializer.instance.shop = self.kwargs["shop_id"]

    @cached_property
    def basket_data(self) -> Dict:
        # input data contains verified model objects
        serializer = OrderFromBasketSerializer(
            data=self.request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def get_queryset(self) -> QuerySet:
        qs = self.queryset.filter(
            lines__warehouse__shop_id=self.kwargs.get("shop_id"),
        )
        user = self.request.user
        if not (user.is_superuser or user.is_staff):
            qs = qs.filter(buyer=user)
        return qs

    @action(detail=False, methods=("post",), url_path="from-basket")
    def from_basket(
        self, request: Request, shop_id: Union[int, AnyStr], *args, **kwargs
    ) -> Response:
        # check if this outlet is allowed to sell online
        self.check_outlet(shop_id)
        order_data = self.apply_offers(shop_id)

        # massage data
        for line in order_data["lines"]:
            if line["warehouse"] is not None:
                line["warehouse"] = line["warehouse"].pk
                for offer_line in line["offers"]:
                    offer_line["offer"] = offer_line["offer"].pk

        order_data["buyer"] = self.request.user.pk
        order_data["payment_method"] = self.basket_data.get("payment_method")

        # save order data as an order
        serializer = OrderSerializer(
            data=order_data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderPayView(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = []
    http_method_names = ["get", "head"]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        amount = (
            Order.objects.annotate(
                amount=Sum(
                    "lines__discounted_price",
                    output_field=DecimalField(max_digits=9, decimal_places=2),
                )
            )
            .filter(id=instance.pk)
            .first()
            .amount
        )

        res = merchant.registration_order(instance.pk, int(amount * 100))
        bank_order_id = res.get("orderId")
        PaymentResult.objects.create(
            order=instance,
            bank_order_id=bank_order_id,
            payment_status=PaymentResult.PaymentStatuses.STATUS_0,
            amount=amount,
        )
        return Response(res)


class AlfaCallBackView(View):
    def get(self, *args, **kwargs):
        payment_result = PaymentResult.objects.get(order_id=kwargs.get("id"))
        status = merchant.get_status(
            payment_result.bank_order_id, payment_result.order.pk
        )

        payment_result.payment_status = status.get("orderStatus")
        payment_result.result = status
        payment_result.save()

        return HttpResponse("Callback page", content_type="text/plain")
