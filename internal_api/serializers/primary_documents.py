from decimal import Decimal

from drf_writable_nested import NestedCreateMixin
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from products.models import ProductUnit

from .. import models
from .shops import WarehouseRecordSerializer


class ProductionDocumentSerializer(serializers.ModelSerializer):
    """
    Related production records are created in the view. You only need to pass
    a proper `daily_menu_plan` into this serializer.
    """

    warehouse_records = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:productionrecord-list",
        lookup_url_kwarg="document_id",
    )

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
        queryset=ProductUnit.objects,
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
    warehouse_records = InventoryRecordSerializer(many=True, write_only=True)
    warehouse_records_on_read = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:inventoryrecord-list",
        lookup_url_kwarg="document_id",
    )

    class Meta:
        model = models.InventoryDocument
        fields = "__all__"

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["warehouse_records"] = result.pop("warehouse_records_on_read", None)
        return result

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

    warehouse_records = WriteOffRecordSerializer(many=True, write_only=True)
    warehouse_records_on_read = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:writeoffrecord-list",
        lookup_url_kwarg="document_id",
    )

    class Meta:
        model = models.WriteOffDocument
        fields = "__all__"

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["warehouse_records"] = result.pop("warehouse_records_on_read", None)
        return result

    def create(self, validated_data):
        # negate quantity
        for each in validated_data.get("warehouse_records", []):
            each["quantity"] = -each["quantity"]
        return super().create(validated_data)


class ReturnRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WarehouseRecord
        exclude = ("document",)


class ReturnDocumentSerializer(NestedCreateMixin, serializers.ModelSerializer):
    """
    This serializer is basically a copy of `WriteOffDocumentSerializer`.
    """

    warehouse_records = ReturnRecordSerializer(many=True, write_only=True)
    warehouse_records_on_read = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:returnrecord-list",
        lookup_url_kwarg="document_id",
    )

    class Meta:
        model = models.ReturnDocument
        fields = "__all__"

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["warehouse_records"] = result.pop("warehouse_records_on_read", None)
        return result

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
        queryset=ProductUnit.objects,
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
    warehouse_records = ConversionRecordSerializer(many=True, write_only=True)
    warehouse_records_on_read = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:conversionrecord-list",
        lookup_url_kwarg="document_id",
    )

    class Meta:
        model = models.ConversionDocument
        fields = "__all__"

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["warehouse_records"] = result.pop("warehouse_records_on_read", None)
        return result

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

    warehouse_records = MoveRecordSerializer(many=True, write_only=True)
    warehouse_records_on_read = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:moverecord-list",
        lookup_url_kwarg="document_id",
    )
    target_shop = serializers.PrimaryKeyRelatedField(
        queryset=models.Shop.objects,
        write_only=True,
    )

    class Meta:
        model = models.MoveDocument
        fields = "__all__"

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["warehouse_records"] = result.pop("warehouse_records_on_read", None)
        return result

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
        queryset=ProductUnit.objects,
        write_only=True,
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

    class Meta:
        model = models.WarehouseRecord
        fields = ("product_unit", "quantity", "cost", "price")


class ReceiptDocumentSerializer(serializers.ModelSerializer):
    warehouse_records = ReceiptRecordSerializer(many=True, write_only=True)
    warehouse_records_on_read = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:receiptrecord-list",
        lookup_url_kwarg="document_id",
    )
    shop = serializers.PrimaryKeyRelatedField(
        queryset=models.Shop.objects,
        write_only=True,
    )

    class Meta:
        model = models.ReceiptDocument
        fields = "__all__"

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["warehouse_records"] = result.pop("warehouse_records_on_read", None)
        return result

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


class SaleRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WarehouseRecord
        exclude = ("document",)


class SaleDocumentSerializer(NestedCreateMixin, serializers.ModelSerializer):
    warehouse_records = SaleRecordSerializer(many=True, write_only=True)
    warehouse_records_on_read = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:salerecord-list",
        lookup_url_kwarg="document_id",
    )

    class Meta:
        model = models.SaleDocument
        fields = "__all__"

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["warehouse_records"] = result.pop("warehouse_records_on_read", None)
        return result

    def create(self, validated_data):
        # invert quantity (same as write-off)
        for each in validated_data.get("warehouse_records", []):
            each["quantity"] = -each["quantity"]
        return super().create(validated_data)


class CancelDocumentSerializer(serializers.ModelSerializer):
    warehouse_records = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:cancelrecord-list",
        lookup_url_kwarg="document_id",
    )

    class Meta:
        model = models.CancelDocument
        fields = "__all__"
