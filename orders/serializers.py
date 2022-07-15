from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from basket.serializers import BasketSerializer

from .models import Order, OrderLine, OrderLineOffer


class OrderLineOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLineOffer
        exclude = ("line",)


class OrderLineSerializer(serializers.ModelSerializer):
    offers = OrderLineOfferSerializer(many=True)

    class Meta:
        model = OrderLine
        exclude = ("document",)

    def to_representation(self, instance):
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


class OrdersSerializer(serializers.ModelSerializer):
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
