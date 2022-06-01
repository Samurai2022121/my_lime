from django.contrib.auth import get_user_model
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from products.models import ProductUnit
from products.serializers import SimpleProductUnitSerializer
from users.serializers import UserSerializer
from utils.serializers_utils import AuthorMixin

from .models import DailyMenuPlan, MenuDish, TechCard, TechCardProduct


class TechProductSerializer(serializers.ModelSerializer):
    product_unit_on_read = SimpleProductUnitSerializer(
        read_only=True,
        source="product_unit",
    )
    product_unit = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=ProductUnit.objects,
    )

    class Meta:
        model = TechCardProduct
        exclude = ("tech_card",)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["product_unit"] = data.pop("product_unit_on_read")
        return data


class TechCardSerializer(
    AuthorMixin,
    WritableNestedModelSerializer,
    serializers.ModelSerializer,
):
    ingredients = TechProductSerializer(source="tech_products", many=True)
    author = serializers.PrimaryKeyRelatedField(
        label="автор",
        queryset=get_user_model().objects.all(),
        required=False,
        write_only=True,
    )
    author_on_read = UserSerializer(label="автор", read_only=True)

    class Meta:
        model = TechCard
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["author"] = data.pop("author_on_read", None)
        return data


class MenuDishSerializer(serializers.ModelSerializer):
    dish = serializers.PrimaryKeyRelatedField(queryset=TechCard.objects)
    dish_on_read = TechCardSerializer(source="dish", read_only=True)

    class Meta:
        model = MenuDish
        fields = ["dish", "dish_on_read", "quantity", "id"]
        read_only_fields = ["id"]

    def to_representation(self, instance):
        result = super().to_representation(instance)
        # replace `dish` with nested read-only representation
        result["dish"] = result.pop("dish_on_read")
        return result


class DailyMenuSerializer(
    AuthorMixin,
    WritableNestedModelSerializer,
    serializers.ModelSerializer,
):
    menu_dishes = MenuDishSerializer(many=True)
    author = serializers.PrimaryKeyRelatedField(
        label="автор",
        queryset=get_user_model().objects.all(),
        required=False,
        write_only=True,
    )
    author_on_read = UserSerializer(label="автор", read_only=True)

    class Meta:
        model = DailyMenuPlan
        fields = [
            "id",
            "shop",
            "author",
            "author_on_read",
            "menu_dishes",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["author"] = data.pop("author_on_read", None)
        return data


class DailyMenuLayoutSerializer(serializers.Serializer):
    product_name = serializers.CharField()
    unit_name = serializers.CharField()
    total = serializers.DecimalField(max_digits=11, decimal_places=2)
    remaining = serializers.DecimalField(max_digits=11, decimal_places=2)
    to_convert = serializers.DecimalField(max_digits=11, decimal_places=2)
    shortage = serializers.DecimalField(max_digits=11, decimal_places=2)

    class Meta:
        fields = ("product_name", "unit_name", "total", "remaining", "convert")
