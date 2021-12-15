from rest_framework import serializers

from products.models import Product

from . import models


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Shop
        fields = "__all__"


class PersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Personnel
        fields = "__all__"


class WarehouseSerializer(serializers.ModelSerializer):
    code = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = ("id", "code", "name")

    def get_code(self, obj):
        return obj.warehouse.values("id", "remaining")
