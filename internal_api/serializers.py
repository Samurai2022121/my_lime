from decimal import Decimal

from drf_base64.fields import Base64FileField
from drf_writable_nested import NestedCreateMixin, WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_nested.serializers import NestedHyperlinkedIdentityField

from products.models import Product

from . import models


class ShopSerializer(serializers.ModelSerializer):
    warehouses = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:warehouse-list",
        lookup_url_kwarg="shop_id",
    )

    class Meta:
        model = models.Shop
        fields = "__all__"


class PersonnelDocumentSerializer(
    WritableNestedModelSerializer, serializers.ModelSerializer
):
    class Meta:
        model = models.PersonnelDocument
        fields = "__all__"


class PersonnelSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    personnel_document = PersonnelDocumentSerializer(many=True)

    class Meta:
        model = models.Personnel
        fields = "__all__"


class SupplyContractSerializer(
    WritableNestedModelSerializer, serializers.ModelSerializer
):
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=models.Supplier.objects.all()
    )
    contract = Base64FileField()

    class Meta:
        model = models.SupplyContract
        fields = "__all__"


class SupplyContractsSerializer(serializers.Serializer):
    files_supply = SupplyContractSerializer(many=True, write_only=True)

    def create(self, validated_data):
        files = validated_data.pop("files_supply", [])
        files = [models.SupplyContract(**f) for f in files]
        supply_contracts = models.SupplyContract.objects.bulk_create(files)
        return supply_contracts


class SupplierSerializer(
    WritableNestedModelSerializer,
    serializers.ModelSerializer,
):
    supply_contract = SupplyContractSerializer(many=True, read_only=True)

    class Meta:
        model = models.Supplier
        fields = "__all__"


class WarehouseRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WarehouseRecord
        fields = "__all__"


class WarehouseSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product_unit.product.name",
        read_only=True,
    )
    unit_name = serializers.CharField(
        source="product_unit.unit.name",
        read_only=True,
    )
    barcode = serializers.IntegerField(
        source="product_unit.product.barcode",
        read_only=True,
    )
    remaining = serializers.DecimalField(
        read_only=True,
        max_digits=7,
        decimal_places=2,
    )
    recommended_price = serializers.DecimalField(
        read_only=True,
        allow_null=True,
        max_digits=7,
        decimal_places=2,
    )
    supplier = SupplierSerializer(allow_null=True, required=False)
    warehouse_records = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:warehouserecord-list",
        lookup_url_kwarg="warehouse_id",
        parent_lookup_kwargs={"shop_id": "shop__id"},
    )

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
    total = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
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
            product = Product.objects.filter(id=product_id)
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
            product = Product.objects.get(id=product_id)
            if order_position_id:
                models.WarehouseOrderPositions.objects.filter(
                    id=order_position_id
                ).update(product=product, **order_position)
            else:
                models.WarehouseOrderPositions.objects.create(
                    product=product, warehouse_order=instance, **order_position
                )
        return instance


class LegalEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LegalEntities
        fields = "__all__"


class ProductionDocumentSerializer(serializers.ModelSerializer):
    """
    Related production records are created in the view. You only need to pass
    a proper `daily_menu_plan` into this serializer.
    """

    warehouse_records = WarehouseRecordSerializer(many=True, read_only=True)

    class Meta:
        model = models.ProductionDocument
        fields = "__all__"


class InventoryRecordSerializer(serializers.ModelSerializer):
    """
    Creates inventory records inside inventory document.

    Inventory records are essentially `WarehouseRecord` objects, but the
    corresponding `Warehouse` object may not exist, hence the use of
    `Manager.get_or_create()`.

    All records in the inventory document must be of the same shop, that's
    why the `Shop` object is passed from the parent serializer through
    the context.
    """

    product_unit = serializers.PrimaryKeyRelatedField(
        queryset=models.ProductUnit.objects,
        write_only=True,
    )
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=models.Supplier.objects,
        write_only=True,
        allow_null=True,
        required=False,
    )
    cost = serializers.DecimalField(
        required=False,
        allow_null=True,
        decimal_places=2,
        max_digits=7,
    )
    price = serializers.DecimalField(
        write_only=True,
        required=False,
        allow_null=True,
        decimal_places=2,
        max_digits=6,
        max_value=Decimal("9999.99"),
        min_value=Decimal("0.01"),
    )
    margin = serializers.DecimalField(
        write_only=True,
        required=False,
        allow_null=True,
        decimal_places=2,
        max_digits=7,
    )
    warehouse = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.WarehouseRecord
        fields = (
            "product_unit",
            "supplier",
            "warehouse",
            "quantity",
            "price",
            "cost",
            "margin",
        )

    def create(self, validated_data):
        cost = validated_data.get("cost", None)

        # get fields for constructing `Warehouse` object
        product_unit = validated_data.pop("product_unit")
        supplier = validated_data.pop("supplier", None)
        margin = validated_data.pop("margin", None)

        # price can be calculated based on record cost and margin,
        # or set separately. If no price, cost, or margin is provided,
        # the operation can still succeed with existing `Warehouse` object
        price = validated_data.pop(
            "price",
            round(cost * (margin + Decimal(100)) / Decimal(100), 2)
            if margin and cost
            else None,
        )
        warehouse, _ = models.Warehouse.objects.get_or_create(
            product_unit=product_unit,
            supplier=supplier,
            shop=self.context.get("shop", None),
            defaults={"price": price, "margin": margin},
        )
        validated_data["warehouse"] = warehouse
        return super().create(validated_data)


class InventoryDocumentSerializer(NestedCreateMixin, serializers.ModelSerializer):
    shop = serializers.PrimaryKeyRelatedField(
        queryset=models.Shop.objects,
        write_only=True,
    )
    warehouse_records = InventoryRecordSerializer(many=True)

    class Meta:
        model = models.InventoryDocument
        fields = "__all__"

    def create(self, validated_data):
        self.context["shop"] = validated_data.pop("shop")
        return super().create(validated_data)


class WriteOffRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WarehouseRecord
        exclude = ("document",)


class WriteOffDocumentSerializer(NestedCreateMixin, serializers.ModelSerializer):
    """
    Nothing special is going on here. Each write-off line may be created by
    stating `warehouse` Id and `quantity`.
    """

    warehouse_records = WriteOffRecordSerializer(many=True)

    class Meta:
        model = models.WriteOffDocument
        fields = "__all__"

    def create(self, validated_data):
        # negate quantity
        for each in validated_data.get("warehouse_records", []):
            each["quantity"] = -each["quantity"]
        return super().create(validated_data)


class ConversionRecordSerializer(serializers.ModelSerializer):
    """
    Gathers data to convert `Warehouse` to target warehouse, which in turn
    may not exist.
    """

    target_unit = serializers.PrimaryKeyRelatedField(
        queryset=models.ProductUnit.objects,
        write_only=True,
    )
    target_supplier = serializers.PrimaryKeyRelatedField(
        queryset=models.Supplier.objects,
        write_only=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = models.WarehouseRecord
        fields = (
            "target_unit",
            "target_supplier",
            "warehouse",
            "quantity",
            "cost",
        )


class ConversionDocumentSerializer(serializers.ModelSerializer):
    warehouse_records = ConversionRecordSerializer(many=True)

    class Meta:
        model = models.ConversionDocument
        fields = "__all__"

    def create(self, validated_data):
        source_records = validated_data.pop("warehouse_records", [])
        document = super().create(validated_data)
        for source_record in source_records:
            target_unit = source_record.pop("target_unit")
            target_supplier = source_record.pop("target_supplier", None)
            source_warehouse = source_record["warehouse"]
            source_quantity = source_record["quantity"]
            source_cost = source_record.get("cost", None)

            # source and target product units must belong to the same product
            source_unit = source_warehouse.product_unit
            if source_unit.product != target_unit.product:
                raise ValidationError("Product mismatch.")

            conversion_qs = source_unit.conversion_sources.filter(
                target_unit=target_unit,
            )
            if conversion_qs.count() > 1:
                raise ValidationError("Ambiguous conversion.")

            conversion = conversion_qs.first()
            if conversion is None:
                raise ValidationError("No way to convert.")

            target_warehouse, _ = models.Warehouse.objects.get_or_create(
                product_unit=target_unit,
                supplier=target_supplier,
                shop=source_warehouse.shop,
                defaults={
                    "price": round(source_warehouse.price / conversion.factor, 2),
                    "margin": source_warehouse.margin,
                },
            )

            target_record = {
                "warehouse": target_warehouse.id,
                "quantity": round(source_quantity * conversion.factor, 2),
                "cost": round(source_cost / conversion.factor, 2)
                if source_cost
                else None,
                "document": document.id,
            }
            # write off initially supplied quantity
            source_record = {
                "warehouse": source_warehouse.id,
                "quantity": -source_quantity,
                "cost": source_cost,
                "document": document.id,
            }
            for data in (source_record, target_record):
                serializer = WarehouseRecordSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return document


class MoveRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WarehouseRecord
        exclude = ("document",)


class MoveDocumentSerializer(serializers.ModelSerializer):
    """
    Doubles the `WarehouseRecord` lines while negating their quantities
    similar to `ConversionDocumentSerializer`, but targets another shop.
    """

    warehouse_records = MoveRecordSerializer(many=True)
    target_shop = serializers.PrimaryKeyRelatedField(
        queryset=models.Shop.objects,
        write_only=True,
    )

    class Meta:
        model = models.MoveDocument
        fields = "__all__"

    def create(self, validated_data):
        source_records = validated_data.pop("warehouse_records", [])
        target_shop = validated_data.pop("target_shop")
        document = super().create(validated_data)
        for source_record in source_records:
            product_unit = source_record["warehouse"].product_unit
            supplier = source_record["warehouse"].supplier
            target_warehouse, _ = models.Warehouse.objects.get_or_create(
                product_unit=product_unit,
                supplier=supplier,
                shop=target_shop,
                defaults={
                    "price": source_record["warehouse"].price,
                    "margin": source_record["warehouse"].margin,
                },
            )
            target_record = source_record.copy()
            target_record["warehouse"] = target_warehouse.id
            target_record["document"] = document.id
            source_record = {
                "warehouse": source_record["warehouse"].id,
                "quantity": -source_record["quantity"],
                "document": document.id,
            }
            for data in (source_record, target_record):
                serializer = WarehouseRecordSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return document


class ReceiptRecordSerializer(serializers.ModelSerializer):
    product_unit = serializers.PrimaryKeyRelatedField(
        queryset=models.ProductUnit.objects,
        write_only=True,
    )
    warehouse = serializers.PrimaryKeyRelatedField(read_only=True)
    price = serializers.DecimalField(
        write_only=True,
        required=False,
        allow_null=True,
        decimal_places=2,
        max_digits=6,
        max_value=Decimal("9999.99"),
        min_value=Decimal("0.01"),
    )

    class Meta:
        model = models.WarehouseRecord
        fields = ("product_unit", "warehouse", "quantity", "price")


class ReceiptDocumentSerializer(serializers.ModelSerializer):
    warehouse_records = ReceiptRecordSerializer(many=True)
    shop = serializers.PrimaryKeyRelatedField(
        queryset=models.Shop.objects,
        write_only=True,
    )

    def create(self, validated_data):
        warehouse_records = validated_data.pop("warehouse_records", [])
        shop = validated_data.pop("shop")
        document = super().create(validated_data)
        # deduct supplier object
        supplier = validated_data["order"].supplier
        for record in warehouse_records:
            product_unit = record["product_unit"]
            warehouse, _ = models.Warehouse.objects.get_or_create(
                product_unit=product_unit,
                supplier=supplier,
                shop=shop,
                defaults={"price": record.get("price", None)},
            )
            serializer = WarehouseRecordSerializer(
                data={
                    "warehouse": warehouse.id,
                    "quantity": record["quantity"],
                    "document": document.id,
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return document

    class Meta:
        model = models.ReceiptDocument
        fields = "__all__"


class SaleRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WarehouseRecord
        exclude = ("document",)


class SaleDocumentSerializer(NestedCreateMixin, serializers.ModelSerializer):
    warehouse_records = SaleRecordSerializer(many=True)

    class Meta:
        model = models.SaleDocument
        fields = "__all__"

    def create(self, validated_data):
        # invert quantity (same as write-off)
        for each in validated_data.get("warehouse_records", []):
            each["quantity"] = -each["quantity"]
        return super().create(validated_data)


class CancelRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WarehouseRecord
        exclude = ("document",)


class CancelDocumentSerializer(serializers.ModelSerializer):
    warehouse_records = CancelRecordSerializer(many=True, read_only=True)

    class Meta:
        model = models.CancelDocument
        fields = "__all__"
