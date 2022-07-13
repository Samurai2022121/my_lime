from rest_framework import serializers

from products.models import ProductUnit

from .shops import models


class ProductUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductUnit
        fields = "__all__"


class WarehouseSerializer(serializers.ModelSerializer):

    product_unit = ProductUnitSerializer()

    class Meta:
        model = models.Warehouse
        fields = "__all__"


class ShopSerializer(serializers.ModelSerializer):
    warehouses = WarehouseSerializer(many=True)

    class Meta:
        model = models.Shop
        fields = "__all__"
