from typing import AnyStr, Dict, Union

from django.db.models import QuerySet
from django.utils.functional import cached_property
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from basket.views import OfferMixin
from utils import permissions as perms

from .models import Order
from .serializers import OrderFromBasketSerializer, OrdersSerializer


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
    serializer_class = OrdersSerializer
    lookup_field = "id"
    queryset = Order.objects.all()

    def get_permissions(self):
        permissions = super().get_permissions()
        return permissions

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
        serializer = self.get_serializer(
            data=order_data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
