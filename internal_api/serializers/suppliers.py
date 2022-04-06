from drf_base64.fields import Base64FileField
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from products.models import ProductUnit

from .. import models
from .shops import SimpleProductUnitSerializer


class SupplyContractSerializer(WritableNestedModelSerializer):
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


class SupplierSerializer(WritableNestedModelSerializer):
    supply_contract = SupplyContractSerializer(many=True, read_only=True)

    class Meta:
        model = models.Supplier
        fields = "__all__"


class WarehouseOrderPositionsSerializer(serializers.ModelSerializer):
    product_unit = serializers.PrimaryKeyRelatedField(
        queryset=ProductUnit.objects,
        write_only=True,
    )
    product_unit_on_read = SimpleProductUnitSerializer(
        source="product_unit",
        read_only=True,
    )

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["product_unit"] = result.pop("product_unit_on_read")
        return result

    class Meta:
        model = models.WarehouseOrderPositions
        exclude = ("warehouse_order",)


class WarehouseOrderSerializer(WritableNestedModelSerializer):
    order_positions = WarehouseOrderPositionsSerializer(
        many=True,
        required=False,
        source="warehouse_order_positions",
    )
    supplier_on_read = SupplierSerializer(source="supplier", read_only=True)
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=models.Supplier.objects,
        allow_null=True,
        required=False,
    )
    total = serializers.DecimalField(
        read_only=True,
        max_digits=10,
        decimal_places=2,
    )
    shop_address = serializers.CharField(source="shop.address", read_only=True)
    shop = serializers.PrimaryKeyRelatedField(queryset=models.Shop.objects)
    created_at = serializers.DateTimeField(required=False)

    class Meta:
        model = models.WarehouseOrder
        fields = "__all__"

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["supplier"] = result.pop("supplier_on_read", None)
        return result


class LegalEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LegalEntities
        fields = "__all__"
