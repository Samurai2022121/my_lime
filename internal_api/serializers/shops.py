from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedIdentityField

from products.models import ProductUnit
from products.serializers import SimpleProductUnitSerializer

from .. import models
from .suppliers import SupplierSerializer


class ShopSerializer(serializers.ModelSerializer):
    warehouses = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="internal_api:warehouse-list",
        lookup_url_kwarg="shop_id",
    )

    class Meta:
        model = models.Shop
        fields = "__all__"


class BatchSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(
        read_only=True,
        label="дата создания",
    )

    class Meta:
        model = models.Batch
        fields = "__all__"


class WarehouseRecordSerializer(serializers.ModelSerializer):
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
    vat_rate = serializers.DecimalField(
        read_only=True,
        max_digits=7,
        decimal_places=2,
        label="ставка НДС, %",
    )
    vat_value = serializers.DecimalField(
        read_only=True,
        max_digits=7,
        decimal_places=2,
        label="сумма НДС",
    )

    class Meta:
        model = models.WarehouseRecord
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["batch"] = data.pop("batch_on_read", None)
        return data


class WarehouseSerializer(serializers.ModelSerializer):
    product_unit_on_read = SimpleProductUnitSerializer(
        read_only=True,
        source="product_unit",
    )
    product_unit = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=ProductUnit.objects,
    )
    remaining = serializers.DecimalField(
        read_only=True,
        max_digits=9,
        decimal_places=4,
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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["product_unit"] = data.pop("product_unit_on_read")
        return data


class SimpleWarehouseSerializer(serializers.ModelSerializer):
    product_unit_on_read = SimpleProductUnitSerializer(
        read_only=True,
        source="product_unit",
    )
    product_unit = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=ProductUnit.objects,
    )
    remaining = serializers.DecimalField(
        read_only=True,
        max_digits=9,
        decimal_places=4,
    )
    recommended_price = serializers.DecimalField(
        read_only=True,
        allow_null=True,
        max_digits=7,
        decimal_places=2,
    )
    supplier = SupplierSerializer(allow_null=True, required=False)

    class Meta:
        model = models.Warehouse
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["product_unit"] = data.pop("product_unit_on_read")
        return data


class WarehouseForScalesSerializer(serializers.ModelSerializer):
    barcode = serializers.IntegerField(source="product_unit.barcode")
    for_scales = serializers.BooleanField(source="product_unit.for_scales")
    for_weighing_scales = serializers.BooleanField(
        source="product_unit.for_weighing_scales"
    )
    vat_rate = serializers.DecimalField(
        source="product_unit.vat_rate",
        read_only=True,
        allow_null=True,
        max_digits=7,
        decimal_places=2,
    )
    weight = serializers.DecimalField(
        source="product_unit.weight",
        read_only=True,
        allow_null=True,
        max_digits=9,
        decimal_places=4,
    )
    packing_weight = serializers.DecimalField(
        source="product_unit.packing_weight",
        read_only=True,
        allow_null=True,
        max_digits=9,
        decimal_places=4,
    )
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    unit_id = serializers.IntegerField(source="product_unit.unit.id")
    unit_name = serializers.CharField(source="product_unit.unit.name")
    product_name = serializers.CharField(source="product_unit.product.name")

    class Meta:
        model = models.Warehouse
        fields = (
            "id",
            "price",
            "barcode",
            "for_scales",
            "for_weighing_scales",
            "vat_rate",
            "weight",
            "packing_weight",
            "unit_name",
            "unit_id",
            "category_id",
            "category_name",
            "product_name",
        )
