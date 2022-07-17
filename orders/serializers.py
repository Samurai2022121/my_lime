from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedIdentityField

from basket.serializers import BasketSerializer
from discounts.models import Offer
from discounts.serializers import OfferSerializer

from .models import Order, OrderLine, OrderLineOffer


class OrderLineOfferSerializer(serializers.ModelSerializer):
    """Universal grandchild serializer."""

    offer = serializers.PrimaryKeyRelatedField(
        label="предложение",
        write_only=True,
        queryset=Offer.objects.all(),
    )
    offer_on_read = OfferSerializer(source="offer", label="предложение", read_only=True)

    def create(self, validated_data):
        # line is either provided as an instance from the parent serializer `create()`
        # method, or as an object ID from the view parameters
        if line_id := self.context["view"].kwargs.get("line_id"):
            validated_data["line_id"] = line_id
        return super().create(validated_data)

    class Meta:
        model = OrderLineOffer
        exclude = ("line",)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["offer"] = data.pop("offer_on_read")
        return data


class NestedOrderLineSerializer(serializers.ModelSerializer):
    """
    Child serializer for a nested endpoint set, **without** nested write capability.
    """

    offers = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="orders:orderlineoffer-list",
        lookup_url_kwarg="line_id",
        parent_lookup_kwargs={
            "shop_id": "warehouse__shop__id",
            "order_id": "document__id",
        },
    )

    class Meta:
        model = OrderLine
        exclude = ("document",)

    def create(self, validated_data):
        validated_data["document_id"] = self.context["view"].kwargs["order_id"]
        return super().create(validated_data)

    def to_representation(self, instance):
        # small fix for a weird model layout
        instance = instance.order_line
        return super().to_representation(instance)


class OrderLineSerializer(serializers.ModelSerializer):
    """Nested child serializer, with nested create capability."""

    offers = OrderLineOfferSerializer(many=True)

    class Meta:
        model = OrderLine
        exclude = ("document",)

    def to_representation(self, instance):
        # small fix for a weird model layout
        instance = instance.order_line
        return super().to_representation(instance)

    def create(self, validated_data):
        line_offers = validated_data.pop("offers", [])
        instance = super().create(validated_data)
        for line_offer in line_offers:
            line_offer["line"] = instance
            line_offer_serializer = OrderLineOfferSerializer(context=self.context)
            line_offer_serializer.create(line_offer)
        return instance


class NestedOrderSerializer(serializers.ModelSerializer):
    """
    Root serializer for a nested endpoints, **without** nested write capability.
    """

    buyer = serializers.PrimaryKeyRelatedField(
        label="покупатель",
        queryset=get_user_model().objects.all(),
        required=False,
    )
    lines = NestedHyperlinkedIdentityField(
        label="позиции",
        read_only=True,
        view_name="orders:orderline-list",
        lookup_url_kwarg="order_id",
        parent_lookup_kwargs={
            "shop_id": "shop",
        },
    )

    class Meta:
        model = Order
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    """Nested create-capable serializer."""

    buyer = serializers.PrimaryKeyRelatedField(
        label="покупатель",
        queryset=get_user_model().objects.all(),
        required=False,
    )
    lines = OrderLineSerializer(many=True)

    class Meta:
        model = Order
        fields = "__all__"

    @transaction.atomic
    def create(self, validated_data):
        lines = validated_data.pop("lines", [])
        instance = super().create(validated_data)
        for line in lines:
            line["document"] = instance
            line_serializer = OrderLineSerializer(context=self.context)
            line_serializer.create(line)
        return instance


class OrderFromBasketSerializer(BasketSerializer):
    """Basket-to-order (ProductUnit-to-Warehouse) source serializer."""

    buyer = serializers.PrimaryKeyRelatedField(
        label="покупатель",
        read_only=True,
        required=False,
    )
    payment_method = serializers.ChoiceField(
        label="способ оплаты",
        choices=Order.PAYMENT_METHODS,
    )
    buyer_comment = serializers.CharField(
        label="примечание покупателя",
        allow_null=True,
        required=False,
    )
    staff_comment = serializers.CharField(
        label="примечание исполнителя",
        allow_null=True,
        required=False,
    )
