from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Order


class OrdersSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        label="покупатель",
        queryset=get_user_model().objects.all(),
        required=False,
    )

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
