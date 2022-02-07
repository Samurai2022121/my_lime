from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg
from drf_base64.fields import Base64ImageField
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
    parent_id = serializers.CharField(write_only=True, required=False)
    image = serializers.ImageField(write_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "parents", "parent_id", "image"]

    def get_parents(self, obj):
        serializer = CategorySerializer(instance=obj.parent)
        return serializer.data

    def create(self, validated_data):
        parent_category_id = validated_data.pop("parent_id", None)
        if parent_category_id:
            parent_category = Category.objects.get(id=parent_category_id)
            category = Category.objects.create(parent=parent_category, **validated_data)
        else:
            category = Category.objects.create(**validated_data)
        return category

    def update(self, instance, validated_data):
        parent_category_id = validated_data.pop("parent_id", None)
        parent_category = None
        if parent_category_id:
            parent_category = Category.objects.get(id=parent_category_id)
        validated_data.update({"parent": parent_category})
        instance = super().update(instance, validated_data)
        return instance


class EditProductImagesSerializer(serializers.ModelSerializer):
    image_1000 = Base64ImageField(required=True)

    class Meta:
        model = ProductImages
        fields = ("id", "image_1000", "main", "description", "product")


class BulkEditProductImagesSerializer(serializers.Serializer):
    images = EditProductImagesSerializer(many=True)

    class Meta:
        fields = ("images",)


class BulkUpdateProductImagesSerializer(serializers.Serializer):
    instances = serializers.ListField(child=serializers.JSONField(), required=True)
    product = serializers.IntegerField(required=True)


class ProductImagesSerializer(serializers.ModelSerializer):
    image_1000 = Base64ImageField()

    class Meta:
        model = ProductImages
        fields = ("id", "image_1000", "image_500", "image_150", "main", "description")


class ProductListAdminSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    images = ProductImagesSerializer(many=True, required=False)

    class Meta:
        model = Product
        exclude = "__all__"


class ProductListSerializer(serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    average_star = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    favourite_count = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    category = CategorySerializer()
    images = ProductImagesSerializer(many=True, required=False)

    class Meta:
        model = Product
        exclude = ["is_archive", "is_sorted", "for_scales", "for_own_production"]

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
    reviews = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    category_read = CategorySerializer(read_only=True, source="category")
    images = ProductImagesSerializer(many=True, required=False)
    is_sorted = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Product
        exclude = ["is_archive"]

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        product = Product.objects.create(**validated_data)

        for image in images_data:
            ProductImages.objects.create(product=product, **image)
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", [])

        for image_obj in images_data:
            image_id = image_obj.get("id", "")
            if image_id:
                ProductImages.objects.filter(id=image_id).update(**image_obj)
            else:
                ProductImages.objects.create(product=instance, **image_obj)
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

    def get_reviews(self, obj):
        return Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).values("review", "mark", "created_at", "user__name")

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


class ProductMatrixSerializer(serializers.ModelSerializer):
    product = serializers.IntegerField(source="id")
    product_name = serializers.CharField(source="name")
    margin = serializers.ReadOnlyField(default=0)
    max_remaining = serializers.ReadOnlyField(default=0)
    min_remaining = serializers.ReadOnlyField(default=0)
    remaining = serializers.ReadOnlyField(default=0)
    shop = serializers.ReadOnlyField(default=None)
    supplier = serializers.ReadOnlyField(default=None)
    supplier_email = serializers.ReadOnlyField(default=None)
    supplier_phone = serializers.ReadOnlyField(default=None)
    auto_order = serializers.ReadOnlyField(default=False)

    class Meta:
        model = Product
        fields = (
            "product_name",
            "price",
            "barcode",
            "product",
            "margin",
            "max_remaining",
            "min_remaining",
            "remaining",
            "shop",
            "supplier",
            "supplier_email",
            "supplier_phone",
            "auto_order",
        )


class BulkActionProductImageSerializer(serializers.Serializer):
    image_ids = serializers.ListField(child=serializers.IntegerField(), required=True)
