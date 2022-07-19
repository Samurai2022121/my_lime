from rest_framework import serializers
from django_restql.mixins import DynamicFieldsMixin

from internal_api.models.primary_documents import SaleDocument
from internal_api.serializers.shops import WarehouseRecordSerializer


class SaleDocumentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    goods_sold = serializers.SerializerMethodField()
    warehouse_records = WarehouseRecordSerializer(many=True)

    def get_goods_sold(self, obj):
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<< 1")
        print(obj)
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<< 2")
        return 0

    class Meta:
        model = SaleDocument
        fields = "__all__"


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    quantity = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    margin_percent = serializers.SerializerMethodField()
    margin_sum = serializers.SerializerMethodField()
    average_stock = serializers.SerializerMethodField()

    def get_quantity(self, obj):
        return sum(obj.get("quantity")) / len(obj.get("quantity"))

    def get_cost(self, obj):
        return sum(obj.get("cost")) / len(obj.get("cost"))

    def get_margin_percent(self, obj):
        return (
            (sum(obj.get("margin")) / len(obj.get("margin")))
            if len(obj.get("margin")) > 0
            else 0
        )

    def get_margin_sum(self, obj):
        one_percent = (
            sum(obj.get("quantity"))
            / len(obj.get("quantity"))
            * sum(obj.get("cost"))
            / len(obj.get("cost"))
            / 100
        )
        return (
            (one_percent * sum(obj.get("margin")) / len(obj.get("margin")))
            if len(obj.get("margin")) > 0
            else 0
        )

    def get_average_stock(self, obj):
        return 0
