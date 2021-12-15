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
    shop = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    min_remaining = serializers.SerializerMethodField()
    max_remaining = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    margin = serializers.SerializerMethodField()
    supplier_email = serializers.SerializerMethodField()
    supplier_phone = serializers.SerializerMethodField()
    auto_order = serializers.SerializerMethodField()
    matrix_line_id = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = ("id", "barcode", "name", "shop", "remaining", "min_remaining", "max_remaining",
                  "margin", "supplier_email", "supplier_phone", "auto_order", "supplier", "matrix_line_id")

    def get_shop(self, obj):
        return obj.warehouse.values("shop") or 0

    def get_remaining(self, obj):
        return obj.warehouse.values("remaining") or 0

    def get_min_remaining(self, obj):
        return obj.warehouse.values("min_remaining") or 0

    def get_max_remaining(self, obj):
        return obj.warehouse.values("max_remaining") or 0

    def get_supplier(self, obj):
        return obj.warehouse.values("supplier") or None

    def get_margin(self, obj):
        return obj.warehouse.values("margin") or 0

    def get_supplier_email(self, obj):
        return obj.warehouse.values("supplier_email") or None

    def get_supplier_phone(self, obj):
        return obj.warehouse.values("supplier_phone") or None

    def get_matrix_line_id(self, obj):
        return obj.warehouse.values("id") or None

    def get_auto_order(self, obj):
        return bool(obj.warehouse.values("auto_order"))

