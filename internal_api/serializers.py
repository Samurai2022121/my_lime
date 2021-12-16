from rest_framework import serializers

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
    outlet_name = serializers.CharField(source="outlet.name", read_only=True)
    barcode = serializers.IntegerField(source="outlet.barcode", read_only=True)
    price = serializers.FloatField(source="outlet.price", read_only=True)

    class Meta:
        model = models.Warehouse
        fields = "__all__"
