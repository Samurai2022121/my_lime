from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg
from rest_framework import serializers

from reviews.models import Favourite, Star
from utils.models_utils import Round

from .models import Category, Product, ProductImages


class CategoryListSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "children", "image"]

    def get_children(self, obj):
        serializer = CategoryListSerializer(instance=obj.get_children(), many=True)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    parents = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "parents"]

    def get_parents(self, obj):
        serializer = CategorySerializer(instance=obj.parent)
        return serializer.data


class EditProductImagesSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source="image_1000")

    class Meta:
        model = ProductImages
        fields = ("id", "image", "main", "description", "product")


class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ("id", "image_1000", "image_500", "image_150", "main", "description")


class ProductListSerializer(serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    average_star = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    favourite_count = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    category = CategorySerializer()
    images = ProductImagesSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "price",
            "in_stock",
            "id",
            "weight",
            "stars_count",
            "stared",
            "average_star",
            "is_favourite",
            "favourite_count",
            "discount",
            "discounted_price",
            "carbohydrates",
            "fats",
            "calories",
            "energy",
            "protein",
            "description",
            "expiration_date",
            "production_date",
            "images",
        ]

    def get_stars_count(self, obj):
        return Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).count()

    def get_average_star(self, obj):
        return Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).aggregate(value=Round(Avg("mark")))["value"]

    def get_stared(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and Star.objects.filter(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
                user=user,
            ).exists()
        )

    def get_favourite_count(self, obj):
        return Favourite.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).count()

    def get_is_favourite(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and Favourite.objects.filter(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
                user=user,
            ).exists()
        )

    def get_discounted_price(self, obj):
        return (
            round((obj.price * (1 - obj.discount / 100)), 2) if obj.discount else None
        )


class ProductSerializer(serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    average_star = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    favourite_count = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    category_read = CategorySerializer(read_only=True, source="category")
    images = ProductImagesSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "production_date",
            "images",
            "protein",
            "carbohydrates",
            "fats",
            "calories",
            "energy",
            "barcode",
            "manufacturer",
            "expiration_date",
            "weight",
            "in_stock",
            "id",
            "stars_count",
            "stared",
            "average_star",
            "is_favourite",
            "favourite_count",
            "category",
            "origin",
            "discount",
            "discounted_price",
            "extra_info",
            "images",
            "own_production",
            "created_at",
            "updated_at",
            "category_read",
        ]

    def create(self, validated_data):
        images_data = validated_data.pop("images")
        product = Product.objects.create(**validated_data)

        for image in images_data:
            ProductImages.objects.create(product=product, **image)
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images")

        for image in images_data:
            ProductImages.objects.update_or_create(**image)

        super().update(instance, validated_data)
        return instance

    def get_average_star(self, obj):
        return Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).aggregate(value=Round(Avg("mark")))["value"]

    def get_stars_count(self, obj):
        return Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).count()

    def get_stared(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and Star.objects.filter(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
                user=user,
            ).exists()
        )

    def get_favourite_count(self, obj):
        return Favourite.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).count()

    def get_is_favourite(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and Favourite.objects.filter(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
                user=user,
            ).exists()
        )

    def get_discounted_price(self, obj):
        return (
            round((obj.price * (1 - obj.discount / 100)), 2) if obj.discount else None
        )


class BulkActionProductSerializer(serializers.Serializer):
    product_ids = serializers.ListField(child=serializers.IntegerField(), required=True)


class BulkChangeProductCategorySerializer(BulkActionProductSerializer):
    new_category = serializers.IntegerField(required=True)
