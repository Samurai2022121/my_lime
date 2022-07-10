from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Order, OrderLine, OrderLineOffer


class OrderLineOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLineOffer
        # exclude = ("line",)
        fields = "__all__"


class OrderLineSerializer(serializers.ModelSerializer):
    offers = OrderLineOfferSerializer(many=True)

    class Meta:
        model = OrderLine
        exclude = ("document",)

    def to_representation(self, instance):
        instance = instance.order_line
        return super().to_representation(instance)


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

    def create(self, validated_data):
        acting_user = self.context["request"].user
        is_staff = acting_user.is_superuser or acting_user.is_staff
        if is_staff:
            # allow staff to directly set document's author
            validated_data.setdefault("customer", acting_user)
        else:
            # set current user as an author
            validated_data["customer"] = acting_user
        return super().create(validated_data)
