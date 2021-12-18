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
    product_name = serializers.CharField(source="product.name", read_only=True)
    barcode = serializers.IntegerField(source="product.barcode", read_only=True)
    price = serializers.FloatField(source="product.price", read_only=True)

    class Meta:
        model = models.Warehouse
        fields = "__all__"


class UploadCSVSerializer(serializers.Serializer):
    csv_file = serializers.FileField()
    price_col = serializers.IntegerField()
    name_col = serializers.IntegerField()
    barcode_col = serializers.IntegerField(required=False)
    vat_col = serializers.IntegerField(required=False)
    supplier_col = serializers.IntegerField(required=False)
    measure_unit_col = serializers.IntegerField(required=False)
    quantity_col = serializers.IntegerField(required=False)
    origin_col = serializers.IntegerField(required=False)
    first_row = serializers.IntegerField()
