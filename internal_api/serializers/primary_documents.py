import calendar
import datetime
from collections import OrderedDict
from decimal import Decimal

from drf_writable_nested import NestedCreateMixin
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from products.models import ProductUnit
from utils.serializers_utils import AuthorMixin

from .. import models
from .shops import WarehouseRecordSerializer


class ProductionDocumentSerializer(AuthorMixin, serializers.ModelSerializer):
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


class NewOrExistingBatchMixin(metaclass=serializers.SerializerMetaclass):
    """
    Helps to provide an existing batch or create a new one.

    Use with a document record serializer of receiving kind. Put in front of
    any other parents in serializer class definition.
    """

    FIELDS = (  # not too elegant decision but hey it works
        "batch",
        "batch_on_read",
        "supplier",
        "expiration_date",
        "production_date",
    )

    batch_on_read = serializers.HyperlinkedRelatedField(
        allow_null=True,
        label="партия",
        lookup_url_kwarg="id",
        source="batch",
        read_only=True,
        view_name="internal_api:batch-detail",
    )
    batch = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        label="партия",
        required=False,
        queryset=models.Batch.objects.all(),
        write_only=True,
    )
    supplier = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        label="поставщик",
        queryset=models.Supplier.objects,
        required=False,
        write_only=True,
    )
    expiration_date = serializers.DateField(
        allow_null=True,
        label="годен до",
        required=False,
        write_only=True,
    )
    production_date = serializers.DateField(
        allow_null=True,
        label="дата производства",
        required=False,
        write_only=True,
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["batch"] = data.pop("batch_on_read", None)
        return data

    def provide_new_or_existing_batch(self, data: OrderedDict):
        """Call from `create()` or `update()` method."""
        batch = data.pop("batch", None)
        supplier = data.pop("supplier", None)
        expiration_date = data.pop("expiration_date", None)
        production_date = data.pop("production_date", None)

        # do we have any data to create a new batch object?
        create_batch = any([supplier, production_date, expiration_date])
        if batch and create_batch:
            raise ValidationError(
                "You cannot provide a batch Id and batch attributes"
                " in the same query line."
            )
        if create_batch:
            batch = models.Batch.objects.create(
                supplier=supplier,
                expiration_date=expiration_date,
                production_date=production_date,
            )
        return batch


class InventoryRecordSerializer(
    NewOrExistingBatchMixin,
    serializers.ModelSerializer,
):
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
            "warehouse",
            "quantity",
            "price",
            "cost",
            "margin",
        ) + NewOrExistingBatchMixin.FIELDS

    def create(self, validated_data):
        cost = validated_data.get("cost", None)

        # get fields for constructing `Warehouse` object
        product_unit = validated_data.pop("product_unit")
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
        warehouse, created = models.Warehouse.objects.get_or_create(
            product_unit=product_unit,
            shop=self.context.get("shop", None),
            defaults={"price": price, "margin": margin},
        )
        if not created:
            warehouse.price = price
            warehouse.margin = margin
            warehouse.save()

        validated_data["warehouse"] = warehouse
        validated_data["batch"] = self.provide_new_or_existing_batch(validated_data)
        return super().create(validated_data)


class InventoryDocumentSerializer(
    AuthorMixin, NestedCreateMixin, serializers.ModelSerializer
):
    shop = serializers.PrimaryKeyRelatedField(
        queryset=models.Shop.objects,
        allow_null=True,
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


class ReceiptRecordSerializer(
    NewOrExistingBatchMixin,
    serializers.ModelSerializer,
):
    product_unit = serializers.PrimaryKeyRelatedField(
        queryset=ProductUnit.objects,
        write_only=True,
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

    def create(self, validated_data):
        """Same as `InventoryRecordSerializer.create()`."""
        cost = validated_data.get("cost", None)
        product_unit = validated_data.pop("product_unit")
        margin = validated_data.pop("margin", None)
        price = validated_data.pop(
            "price",
            round(cost * (margin + Decimal(100)) / Decimal(100), 2)
            if margin and cost
            else None,
        )
        warehouse, created = models.Warehouse.objects.get_or_create(
            product_unit=product_unit,
            shop=self.context.get("shop", None),
            defaults={"price": price, "margin": margin},
        )
        if not created:
            warehouse.price = price
            warehouse.margin = margin
            warehouse.save()

        validated_data["warehouse"] = warehouse
        validated_data["batch"] = self.provide_new_or_existing_batch(validated_data)
        return super().create(validated_data)

    class Meta:
        model = models.WarehouseRecord
        fields = (
            "product_unit",
            "warehouse",
            "quantity",
            "cost",
            "price",
            "margin",
        ) + NewOrExistingBatchMixin.FIELDS


class ReceiptDocumentSerializer(
    AuthorMixin, NestedCreateMixin, serializers.ModelSerializer
):
    warehouse_records = ReceiptRecordSerializer(many=True, write_only=True)
    warehouse_records_on_read = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:receiptrecord-list",
        lookup_url_kwarg="document_id",
    )
    shop = serializers.PrimaryKeyRelatedField(
        queryset=models.Shop.objects,
        allow_null=True,
    )

    class Meta:
        model = models.ReceiptDocument
        fields = "__all__"

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["warehouse_records"] = result.pop("warehouse_records_on_read", None)
        return result

    def create(self, validated_data):
        self.context["shop"] = validated_data.pop("shop")
        return super().create(validated_data)


class ExistingBatchMixin(metaclass=serializers.SerializerMetaclass):
    FIELDS = ("batch", "batch_on_read")

    batch_on_read = serializers.HyperlinkedRelatedField(
        allow_null=True,
        label="партия",
        lookup_url_kwarg="id",
        source="batch",
        read_only=True,
        view_name="internal_api:batch-detail",
    )
    batch = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        label="партия",
        required=False,
        queryset=models.Batch.objects.all(),
        write_only=True,
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["batch"] = data.pop("batch_on_read", None)
        return data


class WriteOffRecordSerializer(ExistingBatchMixin, serializers.ModelSerializer):
    class Meta:
        model = models.WarehouseRecord
        fields = ("warehouse", "quantity", "cost") + ExistingBatchMixin.FIELDS

    def create(self, validated_data):
        # negate quantity
        validated_data["quantity"] = -validated_data["quantity"]
        return super().create(validated_data)


class WriteOffDocumentSerializer(
    AuthorMixin, NestedCreateMixin, serializers.ModelSerializer
):
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
    shop = serializers.PrimaryKeyRelatedField(
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = models.WriteOffDocument
        fields = "__all__"

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["warehouse_records"] = result.pop("warehouse_records_on_read", None)
        return result


class ReturnRecordSerializer(ExistingBatchMixin, serializers.ModelSerializer):
    class Meta:
        model = models.WarehouseRecord
        fields = ("warehouse", "quantity", "cost") + ExistingBatchMixin.FIELDS

    def create(self, validated_data):
        # negate quantity
        validated_data["quantity"] = -validated_data["quantity"]
        return super().create(validated_data)


class ReturnDocumentSerializer(
    AuthorMixin, NestedCreateMixin, serializers.ModelSerializer
):
    """
    This serializer is basically a copy of `WriteOffDocumentSerializer`.
    """

    warehouse_records = ReturnRecordSerializer(many=True, write_only=True)
    warehouse_records_on_read = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:returnrecord-list",
        lookup_url_kwarg="document_id",
    )
    shop = serializers.PrimaryKeyRelatedField(
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = models.ReturnDocument
        fields = "__all__"

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["warehouse_records"] = result.pop("warehouse_records_on_read", None)
        return result


class SaleRecordSerializer(ExistingBatchMixin, serializers.ModelSerializer):
    class Meta:
        model = models.WarehouseRecord
        fields = ("warehouse", "quantity", "cost") + ExistingBatchMixin.FIELDS

    def create(self, validated_data):
        # negate quantity
        validated_data["quantity"] = -validated_data["quantity"]
        return super().create(validated_data)


class SaleDocumentSerializer(
    AuthorMixin, NestedCreateMixin, serializers.ModelSerializer
):
    warehouse_records = SaleRecordSerializer(many=True, write_only=True)
    warehouse_records_on_read = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:salerecord-list",
        lookup_url_kwarg="document_id",
    )
    shop = serializers.PrimaryKeyRelatedField(
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = models.SaleDocument
        fields = "__all__"

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["warehouse_records"] = result.pop("warehouse_records_on_read", None)
        return result


class ConversionRecordSerializer(serializers.ModelSerializer):
    """
    Gathers data to convert `Warehouse` to target warehouse, which in turn
    may not exist.
    """

    target_unit = serializers.PrimaryKeyRelatedField(
        queryset=ProductUnit.objects,
        write_only=True,
    )

    class Meta:
        model = models.WarehouseRecord
        fields = (
            "target_unit",
            "warehouse",
            "quantity",
            "cost",
        )


class ConversionDocumentSerializer(AuthorMixin, serializers.ModelSerializer):
    warehouse_records = ConversionRecordSerializer(many=True, write_only=True)
    warehouse_records_on_read = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:conversionrecord-list",
        lookup_url_kwarg="document_id",
    )
    shop = serializers.PrimaryKeyRelatedField(
        read_only=True,
        allow_null=True,
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


class MoveRecordSerializer(ExistingBatchMixin, serializers.ModelSerializer):
    class Meta:
        model = models.WarehouseRecord
        fields = ("warehouse", "quantity", "cost") + ExistingBatchMixin.FIELDS


class MoveDocumentSerializer(AuthorMixin, serializers.ModelSerializer):
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
        allow_null=True,
    )
    source_shop = serializers.PrimaryKeyRelatedField(
        read_only=True,
        allow_null=True,
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
            target_warehouse, _ = models.Warehouse.objects.get_or_create(
                product_unit=product_unit,
                shop=target_shop,
                defaults={
                    "price": source_record["warehouse"].price,
                    "margin": source_record["warehouse"].margin,
                },
            )
            batch = source_record.get("batch", None)
            target_record = source_record.copy()
            target_record["warehouse"] = target_warehouse.id
            target_record["document"] = document.id
            target_record["batch"] = batch.id if batch else None
            source_record = {
                "warehouse": source_record["warehouse"].id,
                "quantity": -source_record["quantity"],
                "batch": batch.id if batch else None,
                "document": document.id,
            }
            for data in (source_record, target_record):
                serializer = WarehouseRecordSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return document


class CancelDocumentSerializer(AuthorMixin, serializers.ModelSerializer):
    warehouse_records = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:cancelrecord-list",
        lookup_url_kwarg="document_id",
    )

    class Meta:
        model = models.CancelDocument
        fields = "__all__"


class GraphAnaliticsSerializer(serializers.Serializer):
    sales = serializers.SerializerMethodField()

    def get_previous_data(self, current_date, period):
        if period in (None, "month", "day"):
            year, month = calendar._prevmonth(current_date.year, current_date.month)
            return sum(
                [
                    sum(
                        (record.cost * record.quantity)
                        for record in doc.warehouse_records.all()
                    )
                    for doc in models.SaleDocument.objects.filter(
                        created_at=datetime.date(year, month, current_date.day)
                    )
                ]
            )
        else:
            previous_data = datetime.date(
                current_date.year, current_date.month, current_date.day
            ) - datetime.timedelta(days=7)
            return sum(
                [
                    sum(
                        (record.cost * record.quantity)
                        for record in doc.warehouse_records.all()
                    )
                    for doc in models.SaleDocument.objects.filter(
                        created_at=previous_data
                    )
                ]
            )

    def get_sales(self, obj):
        period = self._kwargs.get("context").get("request").query_params.get("period")
        result = {}

        for document in self._args[0]:
            if result.get(document.created_at):
                item = result.get(document.created_at)
                current = item.get("current")
                item.update(
                    {
                        "current": (
                            current
                            + sum(
                                (record.cost * record.quantity)
                                for record in document.warehouse_records.all()
                            )
                        )
                    }
                )
                result.update({document.created_at: item})
            else:
                result.update(
                    {
                        str(document.created_at): {
                            "date": document.created_at,
                            "weekday": calendar.weekday(
                                document.created_at.year,
                                document.created_at.month,
                                document.created_at.day,
                            ),
                            "current": sum(
                                (record.cost * record.quantity)
                                for record in document.warehouse_records.all()
                            ),
                            "previous": self.get_previous_data(
                                document.created_at, period
                            ),
                        }
                    }
                )
        return result.values()

    class Meta:
        fields = "__all__"
