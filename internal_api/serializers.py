from rest_framework import serializers

from . import models
from users.models import User

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Shop
        fields = "__all__"


class PersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Personnel
        fields = "__all__"


class SupplyContractSerializer(serializers.ModelSerializer):
    supplier = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = models.SupplyContract
        fields = "__all__"


class SupplierSerializer(serializers.ModelSerializer):
    supply_contracts = SupplyContractSerializer(many=True, read_only=True)

    class Meta:
        model = models.Supplier
        fields = "__all__"


class WarehouseSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    barcode = serializers.IntegerField(source="product.barcode", read_only=True)
    price = serializers.FloatField(source="product.price", read_only=True)
    supplier = SupplierSerializer()

    class Meta:
        model = models.Warehouse
        fields = "__all__"

    def create(self, validated_data):
        supplier = None
        supplier_data = validated_data.pop("supplier", None)
        if supplier_data:
            supplier = models.Supplier.objects.get(id=supplier_data["id"])
        models.WarehouseOrder.objects.create(**validated_data)
        return models.Warehouse.objects.create(**validated_data, supplier=supplier)

    def update(self, instance, validated_data):
        supplier = None
        supplier_data = validated_data.pop("supplier", None)
        if supplier_data:
            supplier = models.Supplier.objects.get(id=supplier_data["id"])
        validated_data.update({"supplier": supplier})
        instance = super().update(instance, validated_data)
        return instance


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


class WarehouseOrderPositionsSerializer(serializers.HyperlinkedModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_barcode = serializers.ReadOnlyField(source="product.barcode")
    product_id = serializers.IntegerField(source="product.id")
    id = serializers.CharField(required=False)

    class Meta:
        model = models.WarehouseOrderPositions
        fields = (
            "product_id",
            "product_name",
            "buying_price",
            "product_barcode",
            "quantity",
            "special",
            "bonus",
            "flaw",
            "id",
            "value_added_tax",
            "value_added_tax_value",
            "margin",
        )


class WarehouseOrderSerializer(serializers.ModelSerializer):
    order_positions = WarehouseOrderPositionsSerializer(
        many=True, source="warehouse_order"
    )
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.IntegerField(write_only=True)
    total = serializers.FloatField(read_only=True)
    shop_address = serializers.CharField(source="shop.address", read_only=True)
    shop_id = serializers.IntegerField(write_only=True)
    created_at = serializers.DateTimeField(required=False)

    class Meta:
        model = models.WarehouseOrder
        fields = "__all__"

    def create(self, validated_data):
        order_positions = validated_data.pop("warehouse_order")
        supplier_id = validated_data.pop("supplier_id")
        shop_id = validated_data.pop("shop_id")
        shop = models.Shop.objects.get(id=shop_id)
        supplier = models.Supplier.objects.get(id=supplier_id)
        validated_data.update({"supplier": supplier, "shop": shop})
        order = models.WarehouseOrder.objects.create(**validated_data)
        for order_position in order_positions:
            product_id = order_position.pop("product")["id"]
            product = models.Product.objects.filter(id=product_id)
            if not product:
                raise serializers.ValidationError(
                    f"Product does {product_id} not exists."
                )
            models.WarehouseOrderPositions.objects.create(
                product=product.first(), warehouse_order=order, **order_position
            )
        return order

    def update(self, instance, validated_data):
        order_positions = validated_data.pop("warehouse_order")
        supplier_id = validated_data.pop("supplier_id")
        shop_id = validated_data.pop("shop_id")
        shop = models.Shop.objects.get(id=shop_id)
        supplier = models.Supplier.objects.get(id=supplier_id)
        validated_data.update({"supplier": supplier, "shop": shop})
        instance = super().update(instance, validated_data)
        for order_position in order_positions:
            product_id = order_position.pop("product")["id"]
            order_position_id = order_position.pop("id", None)
            product = models.Product.objects.get(id=product_id)
            if order_position_id:
                models.WarehouseOrderPositions.objects.filter(
                    id=order_position_id
                ).update(product=product, **order_position)
            else:
                models.WarehouseOrderPositions.objects.create(
                    product=product, warehouse_order=instance, **order_position
                )
        return instance
