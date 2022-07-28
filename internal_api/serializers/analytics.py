from django_restql.mixins import DynamicFieldsMixin
from rest_framework import serializers

from internal_api.models.primary_documents import SaleDocument
from internal_api.models.shops import Batch, Warehouse, WarehouseRecord


class WarehouseSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    shop_address = serializers.CharField(source="shop.address")
    product = serializers.CharField(source="product_unit.product.name")

    class Meta:
        model = Warehouse
        fields = "__all__"


class WarehouseRecordSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
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


class AnalyticsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    quantity = serializers.DecimalField(decimal_places=2, max_digits=6)
    cost = serializers.DecimalField(decimal_places=2, max_digits=6)
    percent = serializers.IntegerField()


class SaleDocumentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    warehouse_records = WarehouseRecordSerializer(many=True)
    analytics = serializers.SerializerMethodField()

    def get_analytics(self, obj):
        products = {}

        for sale_document in self._args[0]:
            warehouse_record = sale_document.warehouse_records.all().prefetch_related(
                "warehouse"
            )
            for warehouse_record in warehouse_record:
                product = products.get(
                    warehouse_record.warehouse.product_unit.product.pk
                )
                if product:
                    quantity = product.get("quantity") + warehouse_record.quantity
                    cost = product.get("cost") + (
                        warehouse_record.cost * warehouse_record.quantity
                    )
                    product.update(
                        {
                            "id": warehouse_record.warehouse.product_unit.product.pk,
                            "name": warehouse_record.warehouse.product_unit.product.name,
                            "quantity": quantity,
                            "cost": cost,
                        }
                    )
                else:
                    products.update(
                        {
                            warehouse_record.warehouse.product_unit.product.pk: {
                                "quantity": warehouse_record.quantity,
                                "cost": warehouse_record.cost
                                * warehouse_record.quantity,
                                "id": warehouse_record.warehouse.product_unit.product.pk,
                                "name": warehouse_record.warehouse.product_unit.product.name,
                            }
                        }
                    )

        total = sum(
            [
                (p_data.get("cost") / p_data.get("quantity"))
                for p_id, p_data in products.items()
            ]
        )
        one_percent = total / 100

        for p_id, p_data in products.items():

            p_data.update(
                {
                    "percent": round(
                        (p_data.get("cost") / p_data.get("quantity")) / one_percent
                    )
                }
            )
            products.update({p_id: p_data})

        return AnalyticsSerializer(list(products.values()), many=True).data

    class Meta:
        model = SaleDocument
        fields = "__all__"
