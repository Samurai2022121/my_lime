from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from .models import DailyMenuPlan, MenuDish, TechCard, TechCardProduct


class TechProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechCardProduct
        fields = "__all__"


class TechCardSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    ingredients = TechProductSerializer(source="tech_products", many=True)

    class Meta:
        model = TechCard
        fields = "__all__"


class MenuDishSerializer(serializers.ModelSerializer):
    dish = TechCardSerializer(read_only=True)

    class Meta:
        model = MenuDish
        fields = ["dish", "quantity", "id"]


class DailyMenuSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    menu_dishes = MenuDishSerializer(many=True)

    class Meta:
        model = DailyMenuPlan
        fields = ["id", "author", "menu_dishes", "created_at", "updated_at"]


class DailyMenuLayoutSerializer(serializers.Serializer):
    product_name = serializers.CharField()
    unit_name = serializers.CharField()
    total = serializers.DecimalField(max_digits=11, decimal_places=2)
    remaining = serializers.DecimalField(max_digits=11, decimal_places=2)
    to_convert = serializers.DecimalField(max_digits=11, decimal_places=2)
    shortage = serializers.DecimalField(max_digits=11, decimal_places=2)

    class Meta:
        fields = ("product_name", "unit_name", "total", "remaining", "convert")
