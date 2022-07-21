from django_restql.mixins import DynamicFieldsMixin
from rest_framework import serializers

from internal_api.models.primary_documents import SaleDocument
from internal_api.models.shops import Batch, Warehouse, WarehouseRecord


class WarehouseSerializer(serializers.ModelSerializer):
    shop_address = serializers.CharField(source="shop.address")
    product = serializers.CharField(source="product_unit.product.name")

    class Meta:
        model = Warehouse
        fields = "__all__"


class WarehouseRecordSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializer()

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
        queryset=Batch.objects.all(),
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
        model = WarehouseRecord
        fields = "__all__"


class SaleDocumentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    goods_sold = serializers.SerializerMethodField()
    warehouse_records = WarehouseRecordSerializer(many=True)

    def get_goods_sold(self, obj):
        return 0

    class Meta:
        model = SaleDocument
        fields = "__all__"
