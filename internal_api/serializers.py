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


class SupplierSerializer(serializers.ModelSerializer):
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
        )


class WarehouseOrderSerializer(serializers.ModelSerializer):
    order_positions = WarehouseOrderPositionsSerializer(
        many=True, source="warehouse_order"
    )
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.IntegerField(write_only=True)
    total = serializers.FloatField(read_only=True)

    class Meta:
        model = models.WarehouseOrder
        fields = "__all__"

    def create(self, validated_data):
        order_positions = validated_data.pop("order_positions", None)
        supplier_id = validated_data.pop("supplier_id")
        supplier = models.Supplier.objects.get(id=supplier_id)
        order = models.WarehouseOrder.objects.create(**validated_data, supplier=supplier)
        for order_position in order_positions:
            product_id = order_position.pop("product_id")
            product = models.Product.objects.get(id=product_id)
            order_position_instance = models.WarehouseOrderPositions.objects.create(
                product=product, **order_position
            )
            order.order_positions.add(order_position_instance)
        return order

    def update(self, instance, validated_data):
        order_positions = validated_data.pop("order_positions", None)
        supplier_id = validated_data.pop("supplier_id")
        supplier = models.Supplier.objects.get(id=supplier_id)
        validated_data.update({"supplier": supplier})
        for order_position in order_positions:
            product_id = order_position.pop("product_id")
            order_id = order_position.pop("id", None)
            product = models.Product.objects.get(id=product_id)
            if order_id:
                models.WarehouseOrderPositions.objects.filter(id=order_id).update(
                    product=product, **order_position
                )
            else:
                new_order_position = models.WarehouseOrderPositions.objects.create(
                    product=product, **order_position
                )
                instance.order_positions.add(new_order_position)
        instance = super().update(instance, validated_data)
        return instance
